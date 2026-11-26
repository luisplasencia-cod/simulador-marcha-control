# Actuonix and Glideforce 50mm-stroke linear actuators with potentiometer feedback

## Which Actuonix and Glideforce models offer 50mm stroke with potentiometer feedback (not Hall, not no-feedback)?

### Takeaway
Both lines offer multiple 50mm (or "2 in / 1.97 in actual" ≈ 50mm) potentiometer-feedback models, but they fall into two clusters: Actuonix's micro lines (PQ12/L12/L16/P16, and Glideforce's micro GF01) are low-force (≤300N) and generally slow; Glideforce's light-duty LACT2P line is high-force (up to 500N) but slow; Glideforce's high-speed GF23 line is fast but low-force (~118N). No single model combines high force and high speed at 50mm with potentiometer feedback (see next question).

### Cited Findings
- **Actuonix L12-P**, part **L12-50-50-12-I** (the "-P" potentiometer suffix is sometimes rendered "-I" in distributor part numbers; DigiKey lists feedback type = Potentiometer): stroke 1.969 in (50.00 mm), dynamic load force 4.95 lbf (22.0 N), static load force 44.96 lbf (200.0 N), speed 0.98 in/s (25.0 mm/s), 12 VDC, duty cycle 20%, IP54 — [DigiKey](https://www.digikey.com/en/products/detail/actuonix-motion-devices-inc/P16-50-256-12-P/12317383) (reseller listing, redirected to the L12 part when the P16-256 part number was queried; weight not listed on this page).
- **Actuonix L12-P 50mm family** also includes a 50:1 gear option per a Turkish reseller mirroring the Actuonix line: "actuonix linear actuator l12-50-50-6-p potentiometer feedback" (6V variant) — [robotsepeti.com listing title](https://www.robotsepeti.com/actuonix-linear-actuator-l12-50-50-6-p-potentiometer-feedback) (reseller, not independently verified against a datasheet page in this session).
- **Actuonix L16-P**, 50mm stroke, three gear ratios, from the Actuonix L16 datasheet PDF (hosted by RobotShop, originating as the manufacturer's own datasheet document): 35:1 → max speed (no load) 32 mm/s, max force (lifted) ~50 N; 63:1 → max speed (no load) 20 mm/s, max force ~100 N; 150:1 → max speed (no load) 8 mm/s, max force ~200 N — [Actuonix L16 Datasheet PDF via RobotShop CDN](https://cdn.robotshop.com/media/F/Fir/RB-Fir-111/pdf/ActuonixL16Datasheet.pdf) (PDF text extraction failed in this session's tooling — binary content; the figures above come from a web-search summary of this same PDF's text, not a verified direct re-read; treat as provisional pending re-check with a PDF text extractor).
- **Actuonix L16-P** also reports peak-power and peak-efficiency operating points (same datasheet, same caveat): 35:1 → peak power 50N@16mm/s, peak efficiency 24N@24mm/s; 63:1 → peak power 75N@10mm/s, peak efficiency 38N@15mm/s; 150:1 → peak power 175N@4mm/s, peak efficiency 75N@7mm/s — [same Actuonix L16 datasheet](https://cdn.robotshop.com/media/F/Fir/RB-Fir-111/pdf/ActuonixL16Datasheet.pdf).
- **Actuonix P16-P**, 50mm stroke, part numbers P16-50-22-12-P, P16-50-64-12-P, P16-50-256-12-P (the "-P" suffix = potentiometer feedback, confirmed by DigiKey's "Feedback Type: Potentiometer" field for P16-50-64-12-P) — gear 22:1 → ~46 mm/s, ~50 N; gear 64:1 → ~18 mm/s, ~90 N; gear 256:1 → ~4.8 mm/s, ~300 N (figures per RS Online / DigiKey listings for each part number, cross-checked across two reseller families but NOT independently re-confirmed against the actuonix.com datasheet in this session — see Gaps) — [DigiKey P16-50-64-12-P](https://www.digikey.com.br/en/products/detail/actuonix-motion-devices-inc/P16-50-64-12-P/12317382), [RS Online listings summarized via search].
- **Actuonix P16** general: 20% duty cycle, IP54 rating, 105.5 mm closed length, ~95 g weight (reseller-reported aggregate across the P16-50 family) — [RS Online listing summary via search] (reseller source; not confirmed on actuonix.com directly — that site returned HTTP 403 to automated fetch in this session).
- **Actuonix PQ12-P** does NOT offer 50mm — its maximum stroke is 20mm. Confirmed via multiple reseller listings; not a candidate for this requirement — [RobotShop PQ12-P listing](https://www.robotshop.com/products/actuonix-pq12-p-linear-actuator-20mm-1001-12v-potentiometer).
- **Glideforce GF01 "Micro" series** (Pololu/Concentric brand, not Actuonix), 50mm stroke, "-2-66" suffix = feedback potentiometer (confirmed on each Pololu spec page), "-1-66" suffix = limit switches instead: GF01-120505-2-66 → 12V, 2.2 kgf (≈21.6 N), 28 mm/s; GF01-121005-2-66 → 12V, 4.3 kgf (≈42.2 N), 17.6 mm/s; GF01-122105-2-66 → 12V, 8.1 kgf (≈79.4 N), 6 mm/s — [Pololu #4482](https://www.pololu.com/product/4482/specs), [Pololu #4486](https://www.pololu.com/product/4486/specs), [Pololu #4490](https://www.pololu.com/product/4490/specs).
- **Glideforce LACT2P-12V** series (light-duty, 2 in nominal / 1.97 in = 50.0 mm actual usable stroke per Pololu's own spec page — i.e., the actual stroke is 50mm even though marketed as "2 inch"), with built-in feedback potentiometer AND limit switches at each end, three gear ratios: LACT2P-12V-05 → 15 kgf (≈147 N), 1.7 in/s (43.2 mm/s) no-load; LACT2P-12V-10 → 25 kgf (≈245 N), 1.1 in/s (27.9 mm/s) no-load; LACT2P-12V-20 → 50 kgf (≈490–500 N), 0.57 in/s (14.6 mm/s) no-load, 0.48 in/s (12.3 mm/s) at max load — [Pololu #2317](https://www.pololu.com/product/2317), [Pololu #3643](https://www.pololu.com/product/3643/specs), [Pololu #2303/specs](https://www.pololu.com/product/2303/specs) (all Pololu's own spec pages — Pololu writes its own detailed tables, per the researcher brief's note on source reliability).
- **Glideforce LACT2P-12V-20 full spec** (Pololu #2303, manufacturer's own detailed page): stroke nominal 2 in / usable 1.97 in; retracted/extended length 7.68 in / 9.65 in; dynamic (peak) force 50 kgf / 110 lb / 500 N max at 12V; static force up to 250 kgf / 550 lb (page is internally inconsistent, showing "550 lb" in the description vs "500 lb" in a footnote for the static rating); speed no load 0.57 in/s (14.6 mm/s), speed at max load 0.48 in/s (12.3 mm/s); feedback potentiometer + limit switches; weight 1.10 kg; current draw 1.2 A no load / 3.2 A max load / 7 A stall (not meant to stall); duty cycle 25% (1 min on / 4 min off); operating temp -25°C to 65°C; IP65 — [Pololu #2303/specs](https://www.pololu.com/product/2303/specs).
- **Glideforce GF23 "High-Speed LD" series**, 2 in nominal / 1.97 in (5.0 cm) actual stroke, "-3-65" suffix includes feedback potentiometer + limit switches: GF23-120502-3-65 → 12V, 12 kgf (≈117.7 N), 3.3 in/s (84 mm/s) no load, ~75 mm/s at max load; can hold position unpowered against static loads up to 30 kgf — [Pololu #4951](https://www.pololu.com/product/4951/specs) (and companion 6 in and 10 in stroke variants #4955, #4959, not 50mm and thus out of scope here).

### Inferences
- The Actuonix "-P" naming suffix and the Glideforce "-2-66" / "-3-65" suffixes both reliably indicate potentiometer feedback across their respective catalogs, as distinct from "-S" (limit switch) or "-1-66" (limit switch) variants — useful for pattern-matching other stroke/gear combinations not explicitly checked here.
- Glideforce's GF01 micro series and Actuonix's L12/L16/P16/PQ12 series overlap heavily in force/speed class (tens to low hundreds of N, single-digit to tens of mm/s) and appear to be direct competitors for the same niche; Glideforce's LACT2P and GF23 lines occupy a different, heavier-duty niche that Actuonix does not appear to match at 50mm stroke.

### Gaps
- The Actuonix L16 datasheet PDF could not be re-read directly by this session's PDF tooling (binary extraction failed); the force/speed table above relies on a prior web-search-engine summary of that same PDF and should be re-verified by opening the PDF directly (saved locally at the path the WebFetch tool reported, or re-downloaded) before treating it as fully confirmed.
- actuonix.com itself returned HTTP 403 Forbidden to automated fetches in this session (tried for the L16-P and L16 datasheet pages) — none of the Actuonix figures in this note were pulled directly from actuonix.com; all come from reseller pages (RobotShop, DigiKey, RS Online) or a RobotShop-hosted copy of the Actuonix PDF. This is flagged per the task's sourcing requirement — treat Actuonix numbers here as reseller-sourced, not manufacturer-site-sourced, until actuonix.com can be reached (e.g., via a browser tool rather than WebFetch, which may be blocked by bot-detection).
- Could not confirm the exact DigiKey/RS listing for P16-50-256-12-P directly (a DigiKey URL guess instead resolved to an unrelated L12-50-50-12-I part); the "~300N at 4.8mm/s" figure for the 256:1 P16 gear ratio rests on a web-search-engine summary of RS Online listings, not a directly fetched page in this session, and one RS listing phrase ("20lb... 4.8mm/s") suggests a possible unit-conversion inconsistency across reseller pages for this specific part that was not resolved (a direct fetch of the RS page returned HTTP 403).
- Did not check Actuonix's other families (e.g., any "L12" non-standard gear ratios, or whether a higher-force 50mm Actuonix option beyond P16-256 exists) exhaustively — only the families explicitly named in the assignment were checked.

## For each such model, what is the dynamic/peak force (N) and speed at full load (mm/s), and at no load?

### Takeaway
See the table below, consolidating all 50mm potentiometer-feedback models found. Loaded-speed figures are rarely published separately from no-load speed by these manufacturers/resellers — only the Glideforce LACT2P-12V-20 and GF23-120502-3-65 had an explicit "speed at max load" figure found in this research.

### Cited Findings
| Brand | Model | Force (dynamic/peak) | Speed, no load | Speed, at rated/max load | Source |
|---|---|---|---|---|---|
| Actuonix | L12-50-50-12 (-I/-P) | 22.0 N dynamic / 200.0 N static | 25.0 mm/s | not published separately | [DigiKey](https://www.digikey.com/en/products/detail/actuonix-motion-devices-inc/P16-50-256-12-P/12317383) |
| Actuonix | L16-50-35-12-P | ~50 N | 32 mm/s | not found | [Actuonix L16 datasheet PDF](https://cdn.robotshop.com/media/F/Fir/RB-Fir-111/pdf/ActuonixL16Datasheet.pdf) (unverified re-extraction, see Gaps) |
| Actuonix | L16-50-63-12-P | ~100 N | 20 mm/s | not found | same |
| Actuonix | L16-50-150-12-P | ~200 N | 8 mm/s | not found | same |
| Actuonix | P16-50-22-12-P | ~50 N | ~46 mm/s | not found | RS Online / search summary |
| Actuonix | P16-50-64-12-P | ~90 N | ~18 mm/s | not found | [DigiKey](https://www.digikey.com.br/en/products/detail/actuonix-motion-devices-inc/P16-50-64-12-P/12317382) |
| Actuonix | P16-50-256-12-P | ~300 N (unverified, see Gaps) | ~4.8 mm/s | not found | RS Online / search summary |
| Glideforce | GF01-120505-2-66 | 2.2 kgf ≈ 21.6 N | 28 mm/s | not found | [Pololu](https://www.pololu.com/product/4482/specs) |
| Glideforce | GF01-121005-2-66 | 4.3 kgf ≈ 42.2 N | 17.6 mm/s | not found | [Pololu](https://www.pololu.com/product/4486/specs) |
| Glideforce | GF01-122105-2-66 | 8.1 kgf ≈ 79.4 N | 6 mm/s | not found | [Pololu](https://www.pololu.com/product/4490/specs) |
| Glideforce | LACT2P-12V-05 | 15 kgf ≈ 147 N | 1.7 in/s = 43.2 mm/s | not found | [Pololu](https://www.pololu.com/product/2317) |
| Glideforce | LACT2P-12V-10 | 25 kgf ≈ 245 N | 1.1 in/s = 27.9 mm/s | not found | [Pololu](https://www.pololu.com/product/3643/specs) |
| Glideforce | LACT2P-12V-20 | 50 kgf ≈ 490–500 N dynamic / up to 250 kgf (2500 N) static | 0.57 in/s = 14.6 mm/s | 0.48 in/s = 12.3 mm/s | [Pololu](https://www.pololu.com/product/2303/specs) |
| Glideforce | GF23-120502-3-65 | 12 kgf ≈ 117.7 N | 3.3 in/s = 84 mm/s | ~75 mm/s (loaded, per search summary) | [Pololu](https://www.pololu.com/product/4951/specs) |

### Inferences
- Across both brands, at the 50mm stroke length, force and speed trade off almost perfectly inversely via gear ratio — no family escapes this trade-off at this stroke length.

### Gaps
- Loaded-speed (as opposed to no-load speed) is explicitly published by the manufacturer for only 2 of the 14 models found (LACT2P-12V-20 and, per a secondary search summary not independently re-verified, GF23-120502-3-65). For the rest, only no-load speed is available from these sources; actual speed under the target load would need to be read off a force-vs-speed curve in the full PDF datasheet (not accessible in this session for Actuonix; Pololu's pages for the GF01/LACT series were checked but most show only single no-load points, not curves).

## What is the weight of each 50mm variant?

### Takeaway
Weight was found only for two models: Glideforce LACT2P-12V-20 (1.10 kg) and an aggregate ~95 g figure for the Actuonix P16-50 family. No weight figures were found for the Actuonix L12-P, L16-P, or the Glideforce GF01/GF23 50mm variants in this session.

### Cited Findings
- Glideforce LACT2P-12V-20: weight 1.10 kg — [Pololu #2303/specs](https://www.pololu.com/product/2303/specs).
- Actuonix P16-50 family (aggregate, not broken out per gear ratio): ~95 g — RS Online listing summary via search (reseller source, not independently re-fetched).

### Gaps
- No weight figure was located for: Actuonix L12-50-50-12-P/I, Actuonix L16-50 (35/63/150:1), Glideforce GF01 (any of the three 50mm force variants), Glideforce GF23-120502-3-65. These would need to be pulled from the respective datasheet/spec page directly (several of which — actuonix.com pages — were blocked to automated fetch in this session).

## Does any variant reach both ≥294N dynamic force AND ≥18mm/s speed at full load, at 50mm stroke, with potentiometer feedback?

### Takeaway
**No.** None of the 14 models found in this research meets both thresholds simultaneously. The two models that come closest from opposite directions are Actuonix P16-50-256-12-P (≈300 N force, but only ≈4.8 mm/s — far below 18 mm/s) and Glideforce GF23-120502-3-65 (≈84 mm/s no-load / ≈75 mm/s loaded, but only ≈118 N — far below 294 N). This is consistent with the general force-speed trade-off observed across both product lines at this stroke length.

### Cited Findings
- Highest-force 50mm potentiometer-feedback model found: Glideforce LACT2P-12V-20, 50 kgf (≈490–500 N dynamic), but speed only 14.6 mm/s no-load / 12.3 mm/s loaded — [Pololu](https://www.pololu.com/product/2303/specs). This exceeds the 294N force bar but fails the 18mm/s speed bar.
- Highest-speed 50mm potentiometer-feedback model found: Glideforce GF23-120502-3-65, 84 mm/s no-load (≈75 mm/s loaded per search summary), but only 12 kgf (≈118 N) — [Pololu](https://www.pololu.com/product/4951/specs). This exceeds the 18mm/s speed bar but fails the 294N force bar by a wide margin.
- Actuonix's highest-force 50mm option, P16-50-256-12-P (~300 N), runs at only ~4.8 mm/s — [RS Online / search summary, unverified against actuonix.com or a directly-fetched reseller page — see Gaps above].

### Inferences
- Within the product lines actually offered by Actuonix and Glideforce at 50mm stroke with potentiometer feedback, no catalog part satisfies both the force and speed requirement simultaneously as of this research. Meeting both would likely require either a custom/special-order unit, a different actuator technology (e.g., a ball-screw actuator with a larger motor, or an actuator at a slightly different stroke length where a more favorable gear ratio exists), or accepting a stroke length other than exactly 50mm.
- It was not possible in this session to check every intermediate gear ratio Actuonix or Glideforce might offer (e.g., whether an L16-P or P16-P gear ratio between the ones found — such as a ~100:1 — might land closer to both targets); the full datasheet PDF (blocked from direct re-extraction, see Gaps) likely contains continuous force-speed curves that could identify an optimal operating point even on an existing part, short of both thresholds being hard specification lines.

### Gaps
- No intermediate gear ratios beyond those explicitly listed by resellers were checked. The underlying Actuonix datasheets likely include full speed-vs-force curves (not just 2–3 discrete points) that were not successfully extracted in this session due to PDF-tooling and site-blocking issues — a follow-up with direct PDF text extraction or a browser-based fetch of actuonix.com could refine this answer.

## Do these companies ship internationally / to South America, or sell mainly through US/Canada/EU distributors (Robotshop, DigiKey, Pololu)?

### Takeaway
Actuonix (Saanichton, BC, Canada) does not appear to have a confirmed South American distributor — searches turned up only US/international (undifferentiated) distributor pages. Pololu/Glideforce, by contrast, explicitly lists a Peru-based distributor (Paruro.pe, Lima) among several South American resellers, and Pololu's own site advertises "same-day shipping, worldwide" — though it was not confirmed whether that worldwide shipping explicitly covers Peru/South America at standard rates versus via the local distributor only.

### Cited Findings
- Actuonix is based in Saanichton, BC, Canada; GlobalSpec's Actuonix distributor locator shows only "United States" and "International" (undifferentiated) options, with no South American entries found — [GlobalSpec](https://www.globalspec.com/supplier/Distributors/ActuonixMotionDevices).
- RS Online stocks Actuonix products and has country sites for South Africa, Thailand, Malaysia, and the Philippines, among others, but no South American RS Online country site was found carrying Actuonix in this search — [RS Online country listings, via search summary].
- For direct international orders, Actuonix lists sales@actuonix.com and phone 1-888-225-9198 — [Firgelli support page](https://www.firgelliauto.com/es/pages/support) (third-party page listing Actuonix contact info, not actuonix.com itself, which was unreachable in this session).
- Pololu announced South American distributors including **Paruro.pe** in Lima, Peru, alongside **Baú da Eletrônica**, **BUILDBOT**, and **FILIPEFLOP** (Brazil), **IMPORTRONIC** (Quito, Ecuador), and **Eneka** (Montevideo, Uruguay) — [Pololu blog: "New distributors in South America"](https://pololu.com/blog/507/new-distributors-in-south-america).
- Pololu's product pages display "Same-day shipping, worldwide" in the site header — [Pololu #2303](https://www.pololu.com/product/2303/specs) (seen incidentally while fetching spec data; not a dedicated shipping-policy page).

### Inferences
- For a Peru-based buyer, Glideforce/Pololu parts likely have an easier procurement path (either via Pololu's own international shipping or via the Lima-based Paruro.pe distributor) than Actuonix parts, which appear to rely on US/Canada/EU-centric distributors (RobotShop, DigiKey, RS Online) with no confirmed South American presence.

### Gaps
- Did not verify whether the Pololu blog post listing Paruro.pe is current (no date was visible in the fetched content) — distributor relationships can lapse; this should be cross-checked against Pololu's current, live distributor list before relying on it.
- Did not check DigiKey's or RobotShop's shipping policy to Peru specifically (both are generally known to ship worldwide via their own logistics, but this was not confirmed with a source in this session).
- Did not find Actuonix's own international-shipping policy (actuonix.com itself being unreachable); it's possible Actuonix ships directly to South America on request even without a listed regional distributor, but this is unconfirmed.
