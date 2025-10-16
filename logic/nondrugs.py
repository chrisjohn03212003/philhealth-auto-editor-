# logic/nondrugs.py
from docx import Document
from .utils import find_detailed_table, normalize_and_map_items, money_to_decimal, decimal_to_money
from decimal import Decimal

def process_nondrugs(doc_uploaded: Document, doc_template: Document, filename: str):
    """
    Process 'With Non-Drugs' category:
    - map names
    - aggregate non-drug items into 'NonDrugs / Supplies'
    - recompute subtotals, total
    """
    out = doc_template

    uploaded_table = find_detailed_table(doc_uploaded)
    items = []
    if uploaded_table:
        for r in uploaded_table.rows[1:]:
            cells = [c.text.strip() for c in r.cells]
            if len(cells) < 6:
                continue
            particular_raw = cells[3]
            particular = normalize_and_map_items(particular_raw)
            debit = money_to_decimal(cells[5])
            # heuristic: treat items with 'PACK' or 'PC' or obvious supply names as non-drugs
            is_nondrug = any(k in particular_raw.upper() for k in ['PACK', 'PC', 'SOLUSET', 'CANNULA', 'SYRINGE', 'SUPPLY', 'DISPOSABLE', 'BOTTLE'])
            items.append({'particular': particular, 'debit': debit, 'is_nondrug': is_nondrug})

    # aggregate
    non_drugs_total = sum(i['debit'] for i in items if i['is_nondrug'])
    drugs_total = sum(i['debit'] for i in items if not i['is_nondrug'])
    grand_total = non_drugs_total + drugs_total

    # place aggregated values into template summary tables.
    # Heuristic approach: find table cell that contains 'NonDrugs / Supplies' and replace adjacent cell text to the computed value.
    for table in out.tables:
        # find row where first cell contains 'NonDrugs' or 'NonDrugs / Supplies'
        for row in table.rows:
            first = row.cells[0].text if row.cells else ''
            if 'NonDrugs' in first or 'NonDrugs / Supplies' in first:
                # set second cell to computed money
                if len(row.cells) >= 2:
                    row.cells[1].text = decimal_to_money(non_drugs_total)
    # same for totals: find 'TOTAL' row label
    for table in out.tables:
        for row in table.rows:
            if any('TOTAL' in c.text.upper() for c in row.cells):
                # put grand total in last numeric cell
                row.cells[-1].text = decimal_to_money(grand_total)

    output_name = f"edited_nondrugs_{filename}"
    from .utils import ensure_contact_number
    ensure_contact_number(out)

    return out, output_name
