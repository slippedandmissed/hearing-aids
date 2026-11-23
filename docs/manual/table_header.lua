-- bold the header row of every table
function Table(tbl)
  for _, row in ipairs(tbl.head.rows) do
    for _, cell in ipairs(row.cells) do
      cell.contents = pandoc.walk_block(pandoc.Div(cell.contents), {
        Plain = function(b) return pandoc.Plain{pandoc.Strong(b.content)} end,
        Para = function(b) return pandoc.Para{pandoc.Strong(b.content)} end,
      }).content
    end
  end
  return tbl
end

-- roomy spacing for narrow tables, tighter for wide ones (4+ columns)
local function raw(s) return pandoc.RawBlock("latex", s) end
local inner = Table
function Table(tbl)
  tbl = inner(tbl)
  local style = #tbl.colspecs >= 4
    and "\\footnotesize\\setlength{\\tabcolsep}{4pt}\\renewcommand{\\arraystretch}{1.3}"
    or "\\small\\setlength{\\tabcolsep}{7pt}\\renewcommand{\\arraystretch}{1.45}"
  return {raw("\\begingroup" .. style), tbl, raw("\\endgroup")}
end
