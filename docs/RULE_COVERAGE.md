# Rule coverage and review boundary

Status: prototype catalogue `prototype-2026-10`, reviewed for source links on 2026-10-17; not a legal opinion or official enforcement checklist.

## Authoritative starting points

- [Department of Consumer Affairs: Legal Metrology materials and Packaged Commodities Rules](https://consumeraffairs.gov.in/index.php/pages/legal-metrology-act)
- [Department of Consumer Affairs: consolidated Packaged Commodities Rules PDF](https://consumeraffairs.gov.in/public/upload/admin/cmsfiles/whatsnews/Book_on_Legal_Metrology_Packaged_Commodities_Rules%2C2011_with_all_amendments_whatsnews.pdf)
- [FSSAI: Labelling and Display Regulations, 2020](https://www.fssai.gov.in/upload/uploadfiles/files/Comp_Labelling%20Display_Version%20VII_03042025.pdf)
- [FSSAI Labelling & Display amendments index](https://fssai.gov.in/food-law/regulations/amendments/labelling-display)

The Department’s rules page currently lists the 2011 Rules and a series of amendments. This project therefore records every seeded rule as `needs_legal_review`: the source links support a reviewer’s traceability work but do not prove that the implementation is current for a product, package, date, exemption, state, or sector.

## Implemented evidence checks

| Tag | General package | Food | Cosmetics / ointments / pharma | What automation does | Current decision boundary |
| --- | --- | --- | --- | --- | --- |
| Manufacturer | Required | Required | Required | Looks for a readable manufacturer / marketer declaration | Passes presence only; address, role and applicability require review |
| Net quantity | Required | Required | Required | Looks for a readable mass/volume declaration and one small set of potentially misleading phrases | Unit, format, exemptions and prominence require review |
| Manufacturing date | Required in seeded catalogue | Required in seeded catalogue | Required in seeded catalogue | Looks for date-related declaration text | Product-specific expiry/packing rules require review |
| MRP | Required | Required | Required | Looks for a readable MRP/price declaration | Does not calculate a legal font height or decide exceptions |
| Consumer care | Required | Required | Required | Looks for contact/care terms | Content and presentation require review |
| Language check | Required in seeded catalogue | Required in seeded catalogue | Required in seeded catalogue | Not automatically confirmed by the current OCR parser | Remains unresolved unless a reviewer confirms it; script/language presence alone would not prove sector-specific compliance |
| Unit sale price | Conditional | Conditional | Conditional | Marked not applicable until package-type conditions are known | Human applicability decision required |
| FSSAI licence / best-before / veg mark | Not applicable | Seeded required | Not applicable | The rules are seeded for structured review; current parser only recognises FSSAI text | Food-specific validation is not yet complete |
| Batch code | Not seeded for every category | Not seeded for every category | Seeded required | Looks for batch/lot wording | Format and product-specific rules require review |
| BIS mark | Not applicable | Not applicable | Not applicable | Conditional metadata only | Coverage and standard must be established first |

## Verdict semantics

- `PASS`: readable evidence exists for the prototype presence check. It does **not** mean certified compliance.
- `CONFIRMED_VIOLATION`: readable evidence supports one of the narrowly coded defects. This must be reviewed before action.
- `UNRESOLVED`: evidence is missing, unreadable, low confidence, or the rule cannot be checked. The application asks for a close-up or manual confirmation.
- `NOT_APPLICABLE`: a conditional or declared-exemption context prevents the prototype from making a check. It is not proof of an exemption.

No text-height result from an uncalibrated image is used to determine a verdict. The operator-selected institutional/small-package context avoids a false negative finding, but remains subject to legal review.
