from .ParserOrg import ParserOrg, OrgHeader, OrgClock, OrgTable, OrgSourceBlock, OrgText, OrgMath, OrgProperties
from typing import List, Sequence, Tuple, Union, Optional

def link_converter(link: str, name: str) -> str:
    if link.startswith("id:"):
        return f"<a href=\"{name}.html\">{name}</a>"
    return f"<a href=\"{link}\">{name}</a>"

def add_header(title: str) -> List[str]:
    return [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        f"<meta charset=\"utf-8\">",
        f"<title>{title}</title>",
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>',
        "</head>",
        "<body>"
    ]

def add_footer() -> List[str]:
    return [
        "</body>",
        "</html>"
        ]


def export_html(orgfile: str, lnconv=None) -> List[str]:
    result: List[str] = add_header("Org Export")
    if lnconv is None:
        lnconv = link_converter
    with ParserOrg(orgfile, lnconv) as p:
        for item in p.parse():
            if isinstance(item, OrgHeader):
                result.append(f"<h{item.level}>{item.name}</h{item.level}>")
            elif isinstance(item, OrgProperties):
                print(item.values)
            elif isinstance(item, OrgClock):
                pass # do nothing for now
            elif isinstance(item, OrgTable):
                result.append("<table>")
                if item.rows:
                    # Table header
                    result.append("<tr>" + "".join(f"<th>{cell}</th>" for cell in item.rows[0]) + "</tr>")
                    # Table rows
                    for row in item.rows[1:]:
                        result.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
                result.append("</table>")
            elif isinstance(item, OrgSourceBlock):
                result.append(f'<pre><code class="language-{item.language}">')
                result.extend(item.lines)
                result.append("</code></pre>")
            elif isinstance(item, OrgText):
                result.append(item.line  + "<br>")
            elif isinstance(item, OrgMath):
                result.append('\[')
                result.extend(item.lines)
                result.append('\]')
    result.extend(add_footer())
    return result
