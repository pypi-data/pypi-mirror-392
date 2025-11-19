# src/auto_pytest_generator/main.py

import asyncio
import click
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options
from urllib.parse import urlparse
from . import addon
import re
from typing import Sequence

async def start_proxy(port: int, url_prefixes: Sequence[str], response_mode: str = "json"):
    """
    启动 mitmproxy 并只对指定的 URL 前缀进行录制。

    参数:
    - port: 本地监听端口
    - url_prefixes: 可重复的 --url-prefix 参数（例如:
        --url-prefix http://1.2.3.4:8000/api --url-prefix http://5.6.7.8:9000/v1）
      mitmproxy 会被配置为只允许这些 host，另外在 addon 层再基于完整前缀(包含 path)
      进行精确过滤，确保只有匹配前缀的请求会被传给生成器。
    """
    # 1. 解析每个前缀的 host（netloc），并收集用于 mitmproxy Options.allow_hosts 的值
    hosts = []
    normalized_prefixes = []
    for p in url_prefixes:
        try:
            parsed = urlparse(p)
            host = parsed.netloc
            if not host:
                raise ValueError
            hosts.append(host)
            # 保留原始前缀，用于在运行时基于完整 URL 做精确匹配
            normalized_prefixes.append(p)
        except Exception:
            click.secho(f"Error: Invalid --url-prefix '{p}'. 请提供完整 URL，如 'http://example.com/api'.", fg="red")
            return

    # 去重 hosts
    hosts = list(dict.fromkeys(hosts))

    # 2. 配置 mitmproxy 的 allow_hosts，mitmproxy 接受正则表达式列表。
    #    这里我们对 host 进行转义，确保点等字符被正确处理。
    allow_hosts_regex = [re.escape(h) for h in hosts]

    opts = Options(
        listen_host='127.0.0.1',
        listen_port=port,
        # allow_hosts 是一个正则列表，mitmproxy 只会允许匹配这些 host 的流量进入。
        allow_hosts=allow_hosts_regex,
    )

    # 3. 创建 DumpMaster 并加载 addon。我们不直接把 generator_addon 暴露给 master，
    #    而是通过一个中间 FilterAddon 只把匹配任一前缀的请求/响应转发给生成器，
    #    同时也可以在这里扩展静态资源过滤（如果需要）。
    master = DumpMaster(opts, with_termlog=True)

    # 原 generator（保留原始接口，传入第一个前缀作为默认描述）
    # 如果 addon.PytestGenerator 支持多个前缀可以在此调整传参。
    # 为每个 url_prefix 创建一个独立的 PytestGenerator 实例，
    # 并为每个实例注册一个只转发该前缀流量的 FilterAddon。
    # 这样可以确保多个 --url-prefix 的流量都会被各自的 generator 处理并生成用例。
    generators = []
    for p in normalized_prefixes:
        try:
            gen = addon.PytestGenerator(url_prefix=p, response_mode=response_mode)
        except TypeError:
            # 兼容：如果旧版 addon 不接受 response_mode，则退回
            try:
                gen = addon.PytestGenerator(p)
            except Exception:
                raise
        generators.append((p, gen))

    # 静态资源扩展名正则（按需增减）
    STATIC_EXT_PATTERN = r"\.(css|js|jpg|jpeg|png|gif|svg|woff2?|ttf|map|ico|json|xml|eot|otf)(?:[?#]|$)"
    static_re = re.compile(STATIC_EXT_PATTERN, re.IGNORECASE)

    class FilterAddon:
        """
        单一分发器：
        - 跳过静态资源（按扩展名）
        - 将符合各个前缀的 flow 分发给对应的 generator 实例
        这样只需向 mitmproxy 注册一个 addon 实例，避免重复注册同名 addon 导致的错误。
        """
        def __init__(self, prefix_generator_pairs):
            # prefix_generator_pairs: list of (prefix, generator)
            self.pairs = [(str(p), g) for p, g in prefix_generator_pairs]

        def _is_static(self, flow):
            url = getattr(flow.request, "url", "") or getattr(flow.request, "pretty_url", "")
            return bool(static_re.search(url))

        def _matching_generators(self, flow):
            url = getattr(flow.request, "url", "") or getattr(flow.request, "pretty_url", "")
            matches = []
            for prefix, gen in self.pairs:
                if url.startswith(prefix):
                    matches.append(gen)
            return matches

        def request(self, flow):
            if self._is_static(flow):
                return
            matches = self._matching_generators(flow)
            if not matches:
                return
            for gen in matches:
                if hasattr(gen, "request"):
                    try:
                        gen.request(flow)
                    except Exception:
                        # 不让单个 generator 异常影响分发逻辑
                        pass

        def response(self, flow):
            if self._is_static(flow):
                return
            matches = self._matching_generators(flow)
            if not matches:
                return
            for gen in matches:
                if hasattr(gen, "response"):
                    try:
                        gen.response(flow)
                    except Exception:
                        pass

    # 只注册一个分发器实例，内部包含所有 (prefix, generator) 对
    master.addons.add(FilterAddon(generators))

    click.echo(f"[*] Proxy started on 127.0.0.1:{port}")
    click.echo(f"[*] Recording traffic for prefixes: {', '.join(normalized_prefixes)}")

    click.echo(f"[*] Extracted hosts (unescaped): {', '.join(hosts)}")
    click.echo("[*] Only requests to the above hosts whose full URL starts with one of the provided prefixes will be recorded as pytest cases.")
    click.echo("[*] Visit http://mitm.it in your browser to verify the proxy certificate/connection.")

    click.echo("[*] Press Ctrl+C to stop.")

    try:
        await master.run()
    except KeyboardInterrupt:
        master.shutdown()


@click.command()
@click.option('--port', default=7890, help='Proxy listen port', type=int)
@click.option('--url-prefix', required=True, multiple=True,
              help='URL prefix of the target API. Can be provided multiple times, e.g. --url-prefix http://1.2.3.4:8000/api --url-prefix http://5.6.7.8:9000/v1')
@click.option('--response-mode', type=click.Choice(['json', 'text']), default='json',
              help='如何生成 response 断言：json 会把响应解析为 Python dict 并以字面量写出（默认）；text 保持原始文本断言。')
def cli(port, url_prefix, response_mode):
    """
    An auto-recorder for generating Pytest smoke tests from API traffic.
    """
    try:
        import asyncio
        asyncio.run(start_proxy(port, url_prefix, response_mode))
    except (KeyboardInterrupt, RuntimeError):
        pass

    click.echo("\n[*] Proxy server shut down.")
    click.echo("[*] Test cases have been generated in the 'generated_tests' directory.")

if __name__ == '__main__':
    cli()