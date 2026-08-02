(function (global) {
  "use strict";

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, function (char) {
      return ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char];
    });
  }

  function safeLink(href) {
    var value = String(href).trim().replace(/^&lt;|&gt;$/g, "");
    if (/^(?:https?:\/\/|mailto:|#|\/(?!\/))/i.test(value)) return value;
    return "";
  }

  function inlineMarkdown(value) {
    var tokens = [];
    function keep(html) {
      var token = "\u0001MD" + tokens.length + "\u0002";
      tokens.push(html);
      return token;
    }

    var text = escapeHtml(value);
    text = text.replace(/`([^`\n]+)`/g, function (_, code) {
      return keep("<code>" + code + "</code>");
    });
    text = text.replace(/&lt;(https?:\/\/[^\s&]+(?:&amp;[^\s&]+)*)&gt;/gi, function (_, href) {
      var safe = safeLink(href);
      return safe ? keep('<a href="' + safe + '" target="_blank" rel="noopener noreferrer">' + href + "</a>") : _;
    });
    text = text.replace(/\[([^\]\n]+)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)/g, function (whole, label, href) {
      var safe = safeLink(href);
      return safe ? keep('<a href="' + safe + '" target="_blank" rel="noopener noreferrer">' + label + "</a>") : whole;
    });
    text = text.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/__([^_\n]+)__/g, "<strong>$1</strong>");
    text = text.replace(/~~([^~\n]+)~~/g, "<del>$1</del>");
    text = text.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>");
    text = text.replace(/(^|[^_])_([^_\n]+)_(?!_)/g, "$1<em>$2</em>");
    return text.replace(/\u0001MD(\d+)\u0002/g, function (_, index) {
      return tokens[Number(index)] || "";
    });
  }

  function splitTableRow(line) {
    var text = line.trim().replace(/^\|/, "").replace(/\|$/, "");
    var escapedPipe = "\u0003PIPE\u0004";
    return text.replace(/\\\|/g, escapedPipe).split("|").map(function (cell) {
      return cell.trim().replace(new RegExp(escapedPipe, "g"), "|");
    });
  }

  function isTableSeparator(line) {
    var cells = splitTableRow(line);
    return cells.length > 0 && cells.every(function (cell) {
      return /^:?-{3,}:?$/.test(cell);
    });
  }

  function isBlockStart(lines, index) {
    var line = lines[index] || "";
    if (!line.trim()) return true;
    if (/^\s*```/.test(line) || /^#{1,6}\s+/.test(line) || /^\s*>\s?/.test(line)) return true;
    if (/^\s*(?:[-+*]|\d+[.)])\s+/.test(line) || /^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(line)) return true;
    return index + 1 < lines.length && line.indexOf("|") >= 0 && isTableSeparator(lines[index + 1]);
  }

  function renderMarkdown(value) {
    var lines = String(value == null ? "" : value).replace(/\r\n?/g, "\n").split("\n");
    var html = [];
    var index = 0;

    while (index < lines.length) {
      var line = lines[index];
      if (!line.trim()) {
        index += 1;
        continue;
      }

      var fence = line.match(/^\s*```\s*([\w+-]*)\s*$/);
      if (fence) {
        var language = (fence[1] || "").replace(/[^\w+-]/g, "");
        var code = [];
        index += 1;
        while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) {
          code.push(lines[index]);
          index += 1;
        }
        if (index < lines.length) index += 1;
        var className = language ? ' class="language-' + language + '"' : "";
        html.push("<pre><code" + className + ">" + escapeHtml(code.join("\n")) + "</code></pre>");
        continue;
      }

      var heading = line.match(/^(#{1,6})\s+(.+)$/);
      if (heading) {
        var level = heading[1].length;
        html.push("<h" + level + ">" + inlineMarkdown(heading[2].replace(/\s+#+\s*$/, "")) + "</h" + level + ">");
        index += 1;
        continue;
      }

      if (/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
        html.push("<hr>");
        index += 1;
        continue;
      }

      if (index + 1 < lines.length && line.indexOf("|") >= 0 && isTableSeparator(lines[index + 1])) {
        var headers = splitTableRow(line);
        index += 2;
        var rows = [];
        while (index < lines.length && lines[index].trim() && lines[index].indexOf("|") >= 0) {
          rows.push(splitTableRow(lines[index]));
          index += 1;
        }
        html.push("<div class=\"table-scroll\"><table><thead><tr>" + headers.map(function (cell) {
          return "<th>" + inlineMarkdown(cell) + "</th>";
        }).join("") + "</tr></thead><tbody>" + rows.map(function (row) {
          return "<tr>" + headers.map(function (_, cellIndex) {
            return "<td>" + inlineMarkdown(row[cellIndex] || "") + "</td>";
          }).join("") + "</tr>";
        }).join("") + "</tbody></table></div>");
        continue;
      }

      if (/^\s*>\s?/.test(line)) {
        var quote = [];
        while (index < lines.length && /^\s*>\s?/.test(lines[index])) {
          quote.push(lines[index].replace(/^\s*>\s?/, ""));
          index += 1;
        }
        html.push("<blockquote>" + quote.map(inlineMarkdown).join("<br>") + "</blockquote>");
        continue;
      }

      var listMatch = line.match(/^\s*([-+*]|\d+[.)])\s+(.+)$/);
      if (listMatch) {
        var ordered = /^\d/.test(listMatch[1]);
        var tag = ordered ? "ol" : "ul";
        var items = [];
        while (index < lines.length) {
          var item = lines[index].match(/^\s*([-+*]|\d+[.)])\s+(.+)$/);
          if (!item || /^\d/.test(item[1]) !== ordered) break;
          var body = item[2];
          var checkbox = body.match(/^\[([ xX])\]\s+(.*)$/);
          if (checkbox) {
            body = '<input type="checkbox" disabled' + (checkbox[1].toLowerCase() === "x" ? " checked" : "") + "> " + inlineMarkdown(checkbox[2]);
          } else {
            body = inlineMarkdown(body);
          }
          items.push("<li>" + body + "</li>");
          index += 1;
        }
        html.push("<" + tag + ">" + items.join("") + "</" + tag + ">");
        continue;
      }

      var paragraph = [line];
      index += 1;
      while (index < lines.length && !isBlockStart(lines, index)) {
        paragraph.push(lines[index]);
        index += 1;
      }
      html.push("<p>" + paragraph.map(inlineMarkdown).join("<br>") + "</p>");
    }

    return html.join("\n");
  }

  global.ClaudeSeoMarkdown = {
    escapeHtml: escapeHtml,
    render: renderMarkdown
  };
})(typeof globalThis !== "undefined" ? globalThis : window);
