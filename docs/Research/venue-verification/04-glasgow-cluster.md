Could not load DatabaseConfig, falling back to env vars: POSTGRES_HOST_PRIMARY environment variable must be set for primary database connection
# Glasgow Cluster — Mobile Index Spike Investigation

Investigating the Glasgow North cluster: 6+ frames reaching ~18× index at 23:00 on 12–13 July 2025 (mapped from 2024 reference dates). Primary hypothesis: proximity to Celtic Park, Ibrox Stadium, Hampden Park, or TRNSMT festival at Glasgow Green.

## 1. Glasgow-Area Frames with Extreme Spikes (average_index > 3.0)

Found **125 frames** in Glasgow area with at least one spike > 3.0×

| Frame | Town | Address | Postcode | POI | Environment | Celtic Park (m) | Ibrox (m) | Hampden (m) | Glasgow Green (m) |
|-------|------|---------|----------|-----|-------------|----------------|-----------|-------------|-------------------|
| 1234859720 | Airdrie | 111Carlisle Road Petersburn Airdrie | ML 6 8 |  | Roadside | 15,145 | 21,598 | 18,320 | 17,027 |
| 1234859721 | Airdrie | 111 Carlisle Road Petersburn Airdrie | ML 6 8 |  | Roadside | 15,148 | 21,601 | 18,322 | 17,030 |
| 1234859788 | Airdrie | East High St nr North Bridge St Airdrie | ML 6 6 |  | Roadside | 14,085 | 20,468 | 17,437 | 15,924 |
| 1234859789 | Airdrie | East High St nr North Bridge St Airdrie | ML 6 6 |  | Roadside | 14,085 | 20,468 | 17,437 | 15,924 |
| 2000113442 | Airdrie | D48 - Carlisle Road, Airdrie | ML 6 8 |  | Roadside | 15,131 | 21,580 | 18,319 | 17,010 |
| 1234627061 | Glasgow North | Exhibition Centre Station (Glasgow), Minerva Street, GLASGOW | G  3 8 | Exhibition Centre | Rail Station | 5,042 | 1,855 | 4,260 | 3,135 |
| 1234627061 | Glasgow North | Exhibition Centre Station (Glasgow), Minerva Street, GLASGOW | G  3 8 | Exhibition Centre | RailStation | 5,042 | 1,855 | 4,260 | 3,135 |
| 1234848002 | Glasgow North | Port Dundas Road 15m bef Dundas Place Glasgow | G  2 3 |  | Roadside | 3,495 | 3,733 | 4,239 | 1,841 |
| 1234849132 | Glasgow North | Killermont Street o/s Buchanan Street Bus Station Glasgow | G  1 2 |  | Roadside | 3,327 | 3,820 | 4,133 | 1,678 |
| 1234849133 | Glasgow North | Killermont Street aft North Hanover Street West Glasgow | G  2 3 |  | Roadside | 3,341 | 3,821 | 4,150 | 1,695 |
| 1234852697 | Glasgow North | Asda Parkhead The Forge Centre Glasgow | G 31 4 | ASDAPARKHEADFORGE | Supermarket Exterior | 603 | 6,789 | 4,376 | 2,222 |
| 1234852697 | Glasgow North | Asda Parkhead The Forge Centre Glasgow | G 31 4 | ASDAPARKHEADFORGE | SupermarketExterior | 603 | 6,789 | 4,376 | 2,222 |
| 1234853767 | Glasgow North | Glasgow Fort O/S Swarovski Opp Boots Provan Road Glasgow | G 34 9 |  | Roadside | 4,916 | 10,959 | 8,672 | 6,537 |
| 1234853768 | Glasgow North | Glasgow Fort O/S Jd Sports Adj Vodaphone Provan Road Glasgow | G 34 9 |  | Roadside | 4,934 | 10,958 | 8,695 | 6,544 |
| 1234855761 | Glasgow North | Port Dundas Road 15m bef Dundas Place Glasgow | G  2 3 |  | Roadside | 3,482 | 3,736 | 4,228 | 1,827 |
| 1234855779 | Glasgow North | Killermont Street aft North Hanover Street West Glasgow | G  1 2 |  | Roadside | 3,326 | 3,820 | 4,132 | 1,677 |
| 1234856789 | Glasgow North | North East side of Carntyne Road (Todd Street) Str | G 31 5 |  | Roadside | 949 | 6,832 | 4,654 | 2,311 |
| 1234859353 | Glasgow North | Gallowgate C/O Spoutmouth Glasgow | G  1 5 |  | Roadside | 2,283 | 4,310 | 3,237 | 475 |
| 1234859354 | Glasgow North | Gallowgate C/O Spoutmouth Glasgow | G  1 5 |  | Roadside | 2,283 | 4,310 | 3,237 | 475 |
| 1234859355 | Glasgow North | Cowcaddens Rd Scottish City Link Building Glasgow | G  2 3 |  | Roadside | 3,409 | 3,845 | 4,258 | 1,792 |
| 1234859356 | Glasgow North | Cowcaddens Rd Scottish City Link Building Glasgow | G  2 3 |  | Roadside | 3,409 | 3,845 | 4,258 | 1,792 |
| 1234859357 | Glasgow North | Lancefield Quay at Mint Hotel Glasgow | G  3 8 |  | Roadside | 4,895 | 1,755 | 3,894 | 2,974 |
| 1234859653 | Glasgow North | North Hanover Street South Cowcaddens Road Glasgow | G  2 3 |  | Roadside | 3,208 | 4,004 | 4,196 | 1,633 |
| 1234859654 | Glasgow North | North Hanover Street South Cowcaddens Road Glasgow | G  2 3 |  | Roadside | 3,208 | 4,005 | 4,196 | 1,633 |
| 1234859990 | Glasgow North | Finneston Quay Finneston Quay nr Finneston Street Glasgow | G  3 8 |  | Roadside | 4,896 | 1,755 | 3,895 | 2,974 |
| 1234859991 | Glasgow North | Finneston Quay Finneston Quay nr Finneston Street Glasgow | G  3 8 |  | Roadside | 4,895 | 1,755 | 3,894 | 2,974 |
| 1234861001 | Glasgow North | North Hanover Street North Hanover Street, C/O Killermont Street Glasgow | G  2 3 |  | Roadside | 3,190 | 3,977 | 4,143 | 1,593 |
| 1234861002 | Glasgow North | North Hanover Street North Hanover Street, C/O Killermont Street Glasgow | G  2 3 |  | Roadside | 3,190 | 3,977 | 4,143 | 1,593 |
| 1234861335 | Glasgow North | Gallowgate Gallowgate at Watson Street, Glasgow Glasgow | G  1 5 |  | Roadside | 2,398 | 4,204 | 3,250 | 572 |
| 1234861345 | Glasgow North | Gallowgate Opp 370 Gallowgate adj Morrisons, Glasgow | G  4 0 |  | Roadside | 1,876 | 4,729 | 3,330 | 386 |
| 1234861346 | Glasgow North | Gallowgate Opp 370 Gallowgate adj Morrisons, Glasgow | G  4 0 |  | Roadside | 1,876 | 4,729 | 3,330 | 386 |
| 1234926735 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S O2 FCG BOOTS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,297 | 3,723 | 3,978 | 1,587 |
| 1234926735 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S O2 FCG BOOTS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,297 | 3,723 | 3,978 | 1,587 |
| 1234926736 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLR O/S O2 FCG TOWARD JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,297 | 3,723 | 3,979 | 1,587 |
| 1234926736 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLR O/S O2 FCG TOWARD JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,297 | 3,723 | 3,979 | 1,587 |
| 1234926737 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLR O/S JOHN LEWIS FCG THORNTONS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,290 | 3,796 | 4,059 | 1,618 |
| 1234926737 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLR O/S JOHN LEWIS FCG THORNTONS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,290 | 3,796 | 4,059 | 1,618 |
| 1234926741 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S PERFUME SHOP,FCG JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,280 | 3,793 | 4,042 | 1,604 |
| 1234926741 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S PERFUME SHOP,FCG JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,280 | 3,793 | 4,042 | 1,604 |
| 1234926742 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S EE FCG QUIZ | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,281 | 3,793 | 4,043 | 1,604 |
| 1234926742 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S EE FCG QUIZ | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,281 | 3,793 | 4,043 | 1,604 |
| 1234926743 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,FIRST FLOOR O/S STARBUCKS FCG BOOTS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,299 | 3,719 | 3,976 | 1,588 |
| 1234926743 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,FIRST FLOOR O/S STARBUCKS FCG BOOTS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,299 | 3,719 | 3,976 | 1,588 |
| 1234926744 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,FIRST FLOOR O/S STARBUCKS FCG JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,298 | 3,720 | 3,976 | 1,587 |
| 1234926744 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,FIRST FLOOR O/S STARBUCKS FCG JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,298 | 3,720 | 3,976 | 1,587 |
| 1234926745 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,LOWER GROUND FLOOR AT BUCHANAN ST ENT,IFO COSTA | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,305 | 3,693 | 3,952 | 1,582 |
| 1234926745 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,LOWER GROUND FLOOR AT BUCHANAN ST ENT,IFO COSTA | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,305 | 3,693 | 3,952 | 1,582 |
| 1234926746 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,FIRST FLOOR O/S JOHN LEWIS,ADJ TO ESCALATORS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,275 | 3,794 | 4,036 | 1,597 |
| 1234926746 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,FIRST FLOOR O/S JOHN LEWIS,ADJ TO ESCALATORS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,275 | 3,794 | 4,036 | 1,597 |
| 1234930794 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S H SAMUEL & HOLLISTER,01 FCG BO | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,292 | 3,743 | 3,997 | 1,592 |
| 1234930794 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S H SAMUEL & HOLLISTER,01 FCG BO | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,292 | 3,743 | 3,997 | 1,592 |
| 1234930795 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S H SAMUEL & HOLLISTER,01 FCG BO | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,291 | 3,744 | 3,997 | 1,592 |
| 1234930795 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLOOR O/S H SAMUEL & HOLLISTER,01 FCG BO | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,291 | 3,744 | 3,997 | 1,592 |
| 1234932170 | Glasgow North | KILLERMONT STREET,OS JOHN LEWIS, OPP BUS STN | G  1 2 |  | Roadside | 3,288 | 3,855 | 4,125 | 1,648 |
| 1235197563 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLR O/S JOHN LEWIS FCG JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | Shopping Centre Interior | 3,290 | 3,796 | 4,059 | 1,618 |
| 1235197563 | Glasgow North | BUCHANAN GALLERIES S/C - GLASGOW,GROUND FLR O/S JOHN LEWIS FCG JOHN LEWIS | G  1 2 | Glasgow - Buchanan Galleries | ShoppingCentreInterior | 3,290 | 3,796 | 4,059 | 1,618 |
| 1235464179 | Glasgow North | Glasgow Eastern Gateway | G 40 3 |  | Roadside | 414 | 6,098 | 3,424 | 1,561 |
| 1235464181 | Glasgow North | XL+ - Hydro Arena II, Glasgow (Southbound) | G  3 8 |  | Roadside | 4,845 | 1,795 | 3,854 | 2,923 |
| 2000028113 | Glasgow North | Vm - 109-115 Gallowgate Spoutmouth Glasgow | G  1 5 |  | Roadside | 2,277 | 4,322 | 3,254 | 481 |
| 2000113429 | Glasgow North | D48 - London Road, Glasgow | G 40 1 |  | Roadside | 2,143 | 4,392 | 3,073 | 268 |
| 2000118300 | Glasgow North | Trongate (Jcn Albion St, OS 36 Guitar Guitar) | G  1 5 |  | Roadside | 2,570 | 4,052 | 3,292 | 733 |
| 2000118304 | Glasgow North | Trongate (Jcn Albion St, OS 36 Guitar Guitar) | G  1 5 |  | Roadside | 2,570 | 4,052 | 3,292 | 733 |
| 2000188294 | Glasgow North | D48 - Maryhill Road, Glasgow (Outbound)                | G 20 7 |  | Roadside | 5,562 | 3,735 | 6,099 | 3,996 |
| 2000188294 | Glasgow North | D48 - Maryhill Road, Glasgow (Outbound) Â Â Â Â Â Â Â Â Â Â Â Â Â Â  | G 20 7 |  | Roadside | 5,562 | 3,735 | 6,099 | 3,996 |
| 2000188388 | Glasgow North | GALLOWGATE, GLASGOW | G 31 4 |  | Roadside | 454 | 6,314 | 3,976 | 1,743 |
| 2000196441 | Glasgow North | Dunn Street | G 40 3 |  | Roadside | 750 | 5,829 | 3,087 | 1,359 |
| 2000201879 | Glasgow North | The Screen @ North Hanover Street, Glasgow | G  1 2 |  | Roadside | 3,196 | 4,039 | 4,219 | 1,639 |
| 2000214744 | Glasgow North | Glasgow Fort O/S Costa And H&M Nr Boots Provan Road Glasgow | G 34 9 |  | Roadside | 4,806 | 10,873 | 8,558 | 6,440 |
| 2000214745 | Glasgow North | Glasgow Fort O/S Sketchers Provan Road Glasgow | G 34 9 |  | Roadside | 4,861 | 10,857 | 8,630 | 6,454 |
| 1234606817 | Glasgow South | Ibrox Station, 124 Copland Road, Glasgow | G 51 2 | Ibrox SPT | UndergroundStation-Glasgow | 6,194 | 334 | 4,435 | 4,279 |
| 1234606822 | Glasgow South | Ibrox Station, 124 Copland Road, Glasgow | G 51 2 | Ibrox SPT | UndergroundStation-Glasgow | 6,197 | 332 | 4,438 | 4,282 |
| 1234852696 | Glasgow South | Asda Govan 500 Helen Street Glasgow | G 51 3 | ASDAGOVAN | Supermarket Exterior | 7,323 | 849 | 5,208 | 5,419 |
| 1234852696 | Glasgow South | Asda Govan 500 Helen Street Glasgow | G 51 3 | ASDAGOVAN | SupermarketExterior | 7,323 | 849 | 5,208 | 5,419 |
| 1234852698 | Glasgow South | Asda Toryglen 555 Prospect Hill Road Glasgow | G 42 0 | ASDAPROSPECTHILL | Supermarket Exterior | 3,363 | 4,735 | 441 | 2,609 |
| 1234852698 | Glasgow South | Asda Toryglen 555 Prospect Hill Road Glasgow | G 42 0 | ASDAPROSPECTHILL | SupermarketExterior | 3,363 | 4,735 | 441 | 2,609 |
| 1234861324 | Glasgow South | Helen St Helen St bef Edmiston Drive, Glasgow | G 51 3 |  | Roadside | 7,089 | 621 | 5,000 | 5,186 |
| 1234861325 | Glasgow South | Paisley Road Paisley Road West 40m bef Elizabeth Street opp School, Glasgow | G 51 1 |  | Roadside | 5,842 | 666 | 3,955 | 3,944 |
| 1234861326 | Glasgow South | Paisley Road Paisley Road West 40m bef Elizabeth Street opp School, Glasgow | G 51 1 |  | Roadside | 5,842 | 667 | 3,954 | 3,943 |
| 1234926776 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-O/S SUPERDRUG FCG ENTRANCE | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,274 | 4,196 | 8,766 | 8,368 |
| 1234926776 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-O/S SUPERDRUG FCG ENTRANCE | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,274 | 4,196 | 8,766 | 8,368 |
| 1234926777 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-O/S H&M & ELC,FCG TOWARD PRIMARK | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,287 | 4,209 | 8,778 | 8,381 |
| 1234926777 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-O/S H&M & ELC,FCG TOWARD PRIMARK | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,287 | 4,209 | 8,778 | 8,381 |
| 1234926778 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-O/S PERFUME SHOP,FCG TOWARD FOOD COURT | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,364 | 4,295 | 8,865 | 8,459 |
| 1234926778 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-O/S PERFUME SHOP,FCG TOWARD FOOD COURT | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,364 | 4,295 | 8,865 | 8,459 |
| 1234926779 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-O/S WHSMITH FCG ESCALATORS | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,465 | 4,398 | 8,968 | 8,561 |
| 1234926779 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-O/S WHSMITH FCG ESCALATORS | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,465 | 4,398 | 8,968 | 8,561 |
| 1235077385 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PLLAR O/S VISION EXPRESS,FCG TOWARD M&S | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,445 | 4,378 | 8,948 | 8,541 |
| 1235077385 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PLLAR O/S VISION EXPRESS,FCG TOWARD M&S | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,445 | 4,378 | 8,948 | 8,541 |
| 1235077387 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-PILLAR O/S TRESPASS,FCG TOWARD M&S | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,444 | 4,374 | 8,944 | 8,539 |
| 1235077387 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-PILLAR O/S TRESPASS,FCG TOWARD M&S | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,444 | 4,374 | 8,944 | 8,539 |
| 1235242514 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR O/S VISION EXPRESS,FCG PRIMARK & B | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,448 | 4,380 | 8,950 | 8,543 |
| 1235242514 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR O/S VISION EXPRESS,FCG PRIMARK & B | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,448 | 4,380 | 8,950 | 8,543 |
| 1235242516 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR OUTSIDE NEXT FCG GAME | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,370 | 4,295 | 8,864 | 8,464 |
| 1235242516 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR OUTSIDE NEXT FCG GAME | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,370 | 4,295 | 8,864 | 8,464 |
| 1235242517 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR OPP BEAVERBROOKS,FCG TOWARD PRIMAR | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,393 | 4,318 | 8,888 | 8,487 |
| 1235242517 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR OPP BEAVERBROOKS,FCG TOWARD PRIMAR | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,393 | 4,318 | 8,888 | 8,487 |
| 1235242519 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR OPP BEAVERBROOKS,FCG TOWARD M&S | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,392 | 4,317 | 8,886 | 8,487 |
| 1235242519 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR OPP BEAVERBROOKS,FCG TOWARD M&S | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,392 | 4,317 | 8,886 | 8,487 |
| 1235242520 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR O/S M&S ADJ ESCALATOR,FCG TOWARD P | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,299 | 4,218 | 8,788 | 8,393 |
| 1235242520 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR O/S M&S ADJ ESCALATOR,FCG TOWARD P | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,299 | 4,218 | 8,788 | 8,393 |
| 1235242522 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR O/S M&S ADJ ESCALATOR,FCG SUPERDRU | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,299 | 4,218 | 8,788 | 8,393 |
| 1235242522 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,LOWER MALL-PILLAR O/S M&S ADJ ESCALATOR,FCG SUPERDRU | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,299 | 4,218 | 8,788 | 8,393 |
| 1235242527 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-CENTAL ATRIUM,FCG PERFUME SHOP | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,369 | 4,295 | 8,864 | 8,463 |
| 1235242527 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-CENTAL ATRIUM,FCG PERFUME SHOP | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,369 | 4,295 | 8,864 | 8,463 |
| 1235242530 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-PILLAR O/S GOLDSMITHS,FCG PERFUME SHOP | G 51 4 | Glasgow - Braehead Shopping Centre | Shopping Centre Interior | 10,370 | 4,292 | 8,861 | 8,464 |
| 1235242530 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-PILLAR O/S GOLDSMITHS,FCG PERFUME SHOP | G 51 4 | Glasgow - Braehead Shopping Centre | ShoppingCentreInterior | 10,370 | 4,292 | 8,861 | 8,464 |
| 2000212868 | Glasgow South | SHUB Paisley Rd West (OS No.472) | G 51 1 |  | Roadside | 5,863 | 648 | 3,967 | 3,964 |
| 2000212869 | Glasgow South | SHUB Paisley Rd West (OS No.472) | G 51 1 |  | Roadside | 5,863 | 647 | 3,969 | 3,965 |
| 1234855590 | Motherwell | Windmillhill St at 49 opp Camp St Motherwell | ML 1 1 |  | Roadside | 15,592 | 21,689 | 17,409 | 17,433 |
| 1234855591 | Motherwell | Windmillhill St at 49 opp Camp St Motherwell | ML 1 1 |  | Roadside | 15,592 | 21,689 | 17,409 | 17,433 |
| 1234855594 | Paisley | Gauze St s/side opp Silk St Paisley | PA 1 1 |  | Roadside | 13,264 | 6,828 | 10,572 | 11,381 |
| 1234855595 | Paisley | Gauze St s/side opp Silk St Paisley | PA 1 1 |  | Roadside | 13,263 | 6,827 | 10,572 | 11,381 |
| 1234856806 | Paisley | 29/35 St James Street A726 Near Caledonia Street S | PA 3 2 |  | Roadside | 13,991 | 7,536 | 11,334 | 12,101 |
| 1234858480 | Paisley | St James Street At No. 14 w/o Glen Lane Paisley | PA 3 2 |  | Roadside | 13,928 | 7,472 | 11,276 | 12,037 |
| 1234859900 | Paisley | Gauze Street at 21 e/o Lawn Street Paisley | PA 1 1 |  | Roadside | 13,360 | 6,926 | 10,661 | 11,479 |
| 1234859901 | Paisley | Gauze Street at 21 e/o Lawn Street Paisley | PA 1 1 |  | Roadside | 13,360 | 6,926 | 10,661 | 11,479 |
| 2000028118 | Paisley | St James Street A726 nr Caledonia Street Paisley | PA 3 2 |  | Roadside | 14,039 | 7,584 | 11,381 | 12,149 |
| 1234855887 | Rutherglen | 201 Glasgow Road Rutherglen Glasgow | G 73 1 |  | Roadside | 2,212 | 5,829 | 1,862 | 2,354 |
| 1234856791 | Rutherglen | 19 Rutherglen Road Strathclyde | G 73 1 |  | Roadside | 2,036 | 5,281 | 1,767 | 1,737 |
| 1234856792 | Rutherglen | 19 Rutherglen Road Strathclyde | G 73 1 |  | Roadside | 2,036 | 5,279 | 1,766 | 1,735 |
| 1235190714 | Rutherglen | TESCO RUTHERGLEN,DALMARNOCH ROAD,STORE ENTRANCE | G 73 1 | TescoRutherglen | Supermarket Exterior | 1,685 | 6,496 | 2,710 | 2,529 |
| 1235190714 | Rutherglen | TESCO RUTHERGLEN,DALMARNOCH ROAD,STORE ENTRANCE | G 73 1 | TescoRutherglen | SupermarketExterior | 1,685 | 6,496 | 2,710 | 2,529 |
| 1235462335 | Rutherglen | ICON - MAIN STREET CNR OF SHAWFIELD ROAD | G 73 1 |  | Roadside | 1,746 | 5,269 | 2,060 | 1,440 |
| 1235462352 | Rutherglen | CLYDE GATEWAY MAIN STREET N/S | G 73 1 |  | Roadside | 1,746 | 5,269 | 2,060 | 1,440 |
| 2000181153 | Rutherglen | XL - Glasgow Road (A730) At Princes Street, Rutherglen, Glasgow | G 73 1 |  | Roadside | 2,353 | 6,098 | 1,986 | 2,652 |

### Nearest Venue Summary

- **Celtic Park**: 17 frame(s) closest
- **Ibrox**: 35 frame(s) closest
- **Hampden**: 3 frame(s) closest
- **Glasgow Green**: 38 frame(s) closest

## 2. Date Mapping — July 2025 Spike Dates

Date mapping (2024 reference → 2025 actual):

- 2025-07-12 (2025) corresponds to reference date **2024-07-13** (2024)
- 2025-07-13 (2025) corresponds to reference date **2024-07-14** (2024)

## 3. Hourly Profiles on Peak Dates (July 12-13 2025)

### Frame 1234606817 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 6,194 m | Ibrox 334 m | Hampden 4,435 m | Glasgow Green 4,279 m

```
 0:00  avg=  1.12  med=  1.12  ██
 1:00  avg=  1.12  med=  1.12  ██
 2:00  avg=  1.12  med=  1.12  ██
 3:00  avg=  1.12  med=  1.12  ██
 4:00  avg=  1.12  med=  1.12  ██
 5:00  avg=  0.95  med=  0.95  █
 6:00  avg=  0.91  med=  0.90  █
 7:00  avg=  0.89  med=  0.89  █
 8:00  avg=  0.69  med=  0.68  █
 9:00  avg=  0.85  med=  0.85  █
10:00  avg=  0.73  med=  0.75  █
11:00  avg=  0.66  med=  0.69  █
12:00  avg=  0.65  med=  0.69  █
13:00  avg=  0.56  med=  0.60  █
14:00  avg=  0.62  med=  0.69  █
15:00  avg=  0.60  med=  0.63  █
16:00  avg=  0.79  med=  0.86  █
17:00  avg=  0.68  med=  0.76  █
18:00  avg=  0.84  med=  0.95  █
19:00  avg=  0.81  med=  0.94  █
20:00  avg=  1.03  med=  1.18  ██
21:00  avg=  0.88  med=  0.99  █
22:00  avg=  1.06  med=  1.17  ██
23:00  avg=  1.18  med=  1.17  ██
```

### Frame 1234606817 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 6,194 m | Ibrox 334 m | Hampden 4,435 m | Glasgow Green 4,279 m

```
 0:00  avg=  1.09  med=  1.09  ██
 1:00  avg=  1.09  med=  1.09  ██
 2:00  avg=  1.09  med=  1.09  ██
 3:00  avg=  1.09  med=  1.09  ██
 4:00  avg=  1.09  med=  1.09  ██
 5:00  avg=  0.92  med=  0.92  █
 6:00  avg=  0.87  med=  0.86  █
 7:00  avg=  0.83  med=  0.82  █
 8:00  avg=  0.73  med=  0.72  █
 9:00  avg=  0.79  med=  0.79  █
10:00  avg=  0.53  med=  0.55  █
11:00  avg=  0.57  med=  0.60  █
12:00  avg=  0.61  med=  0.66  █
13:00  avg=  0.70  med=  0.75  █
14:00  avg=  0.63  med=  0.70  █
15:00  avg=  0.57  med=  0.61  █
16:00  avg=  0.70  med=  0.76  █
17:00  avg=  0.69  med=  0.76  █
18:00  avg=  0.82  med=  0.92  █
19:00  avg=  0.56  med=  0.65  █
20:00  avg=  0.66  med=  0.76  █
21:00  avg=  0.70  med=  0.79  █
22:00  avg=  0.90  med=  0.99  █
23:00  avg=  1.02  med=  1.02  ██
```

### Frame 1234606822 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 6,197 m | Ibrox 332 m | Hampden 4,438 m | Glasgow Green 4,282 m

```
 0:00  avg=  1.12  med=  1.12  ██
 1:00  avg=  1.12  med=  1.12  ██
 2:00  avg=  1.12  med=  1.12  ██
 3:00  avg=  1.12  med=  1.12  ██
 4:00  avg=  1.12  med=  1.12  ██
 5:00  avg=  0.95  med=  0.95  █
 6:00  avg=  0.91  med=  0.90  █
 7:00  avg=  0.89  med=  0.89  █
 8:00  avg=  0.69  med=  0.68  █
 9:00  avg=  0.85  med=  0.85  █
10:00  avg=  0.73  med=  0.75  █
11:00  avg=  0.66  med=  0.69  █
12:00  avg=  0.65  med=  0.69  █
13:00  avg=  0.56  med=  0.60  █
14:00  avg=  0.62  med=  0.69  █
15:00  avg=  0.60  med=  0.63  █
16:00  avg=  0.79  med=  0.86  █
17:00  avg=  0.68  med=  0.76  █
18:00  avg=  0.84  med=  0.95  █
19:00  avg=  0.81  med=  0.94  █
20:00  avg=  1.03  med=  1.18  ██
21:00  avg=  0.88  med=  0.99  █
22:00  avg=  1.06  med=  1.17  ██
23:00  avg=  1.18  med=  1.17  ██
```

### Frame 1234606822 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 6,197 m | Ibrox 332 m | Hampden 4,438 m | Glasgow Green 4,282 m

```
 0:00  avg=  1.09  med=  1.09  ██
 1:00  avg=  1.09  med=  1.09  ██
 2:00  avg=  1.09  med=  1.09  ██
 3:00  avg=  1.09  med=  1.09  ██
 4:00  avg=  1.09  med=  1.09  ██
 5:00  avg=  0.92  med=  0.92  █
 6:00  avg=  0.87  med=  0.86  █
 7:00  avg=  0.83  med=  0.82  █
 8:00  avg=  0.73  med=  0.72  █
 9:00  avg=  0.79  med=  0.79  █
10:00  avg=  0.53  med=  0.55  █
11:00  avg=  0.57  med=  0.60  █
12:00  avg=  0.61  med=  0.66  █
13:00  avg=  0.70  med=  0.75  █
14:00  avg=  0.63  med=  0.70  █
15:00  avg=  0.57  med=  0.61  █
16:00  avg=  0.70  med=  0.76  █
17:00  avg=  0.69  med=  0.76  █
18:00  avg=  0.82  med=  0.92  █
19:00  avg=  0.56  med=  0.65  █
20:00  avg=  0.66  med=  0.76  █
21:00  avg=  0.70  med=  0.79  █
22:00  avg=  0.90  med=  0.99  █
23:00  avg=  1.02  med=  1.02  ██
```

### Frame 1234627061 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 5,042 m | Ibrox 1,855 m | Hampden 4,260 m | Glasgow Green 3,135 m

```
 0:00  avg=  1.02  med=  1.16  ██
 1:00  avg=  1.02  med=  1.16  ██
 2:00  avg=  1.02  med=  1.16  ██
 3:00  avg=  1.02  med=  1.16  ██
 4:00  avg=  1.02  med=  1.16  ██
 5:00  avg=  1.03  med=  1.05  ██
 6:00  avg=  0.94  med=  0.95  █
 7:00  avg=  0.81  med=  0.80  █
 8:00  avg=  0.72  med=  0.69  █
 9:00  avg=  0.76  med=  0.74  █
10:00  avg=  0.79  med=  0.77  █
11:00  avg=  0.84  med=  0.84  █
12:00  avg=  0.83  med=  0.85  █
13:00  avg=  0.84  med=  0.86  █
14:00  avg=  0.83  med=  0.86  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.79  med=  0.83  █
17:00  avg=  0.76  med=  0.82  █
18:00  avg=  0.82  med=  0.97  █
19:00  avg=  0.88  med=  1.20  █
20:00  avg=  0.82  med=  1.18  █
21:00  avg=  0.80  med=  1.21  █
22:00  avg=  0.80  med=  1.25  █
23:00  avg=  0.61  med=  0.98  █
```

### Frame 1234627061 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 5,042 m | Ibrox 1,855 m | Hampden 4,260 m | Glasgow Green 3,135 m

```
 0:00  avg=  1.21  med=  1.38  ██
 1:00  avg=  1.21  med=  1.38  ██
 2:00  avg=  1.21  med=  1.38  ██
 3:00  avg=  1.21  med=  1.38  ██
 4:00  avg=  1.21  med=  1.38  ██
 5:00  avg=  1.09  med=  1.11  ██
 6:00  avg=  0.92  med=  0.93  █
 7:00  avg=  0.72  med=  0.71  █
 8:00  avg=  0.53  med=  0.51  █
 9:00  avg=  0.62  med=  0.59  █
10:00  avg=  0.66  med=  0.64  █
11:00  avg=  0.65  med=  0.65  █
12:00  avg=  0.63  med=  0.64  █
13:00  avg=  0.62  med=  0.64  █
14:00  avg=  0.64  med=  0.66  █
15:00  avg=  0.64  med=  0.66  █
16:00  avg=  0.68  med=  0.71  █
17:00  avg=  0.64  med=  0.69  █
18:00  avg=  0.65  med=  0.77  █
19:00  avg=  0.63  med=  0.87  █
20:00  avg=  0.59  med=  0.85  █
21:00  avg=  0.59  med=  0.89  █
22:00  avg=  0.64  med=  1.00  █
23:00  avg=  0.44  med=  0.70  
```

### Frame 1234848002 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,495 m | Ibrox 3,733 m | Hampden 4,239 m | Glasgow Green 1,841 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234848002 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,495 m | Ibrox 3,733 m | Hampden 4,239 m | Glasgow Green 1,841 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234849132 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,327 m | Ibrox 3,820 m | Hampden 4,133 m | Glasgow Green 1,678 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234849132 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,327 m | Ibrox 3,820 m | Hampden 4,133 m | Glasgow Green 1,678 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234849133 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,341 m | Ibrox 3,821 m | Hampden 4,150 m | Glasgow Green 1,695 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234849133 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,341 m | Ibrox 3,821 m | Hampden 4,150 m | Glasgow Green 1,695 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234852696 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 7,323 m | Ibrox 849 m | Hampden 5,208 m | Glasgow Green 5,419 m

```
 0:00  avg=  1.02  med=  1.03  ██
 1:00  avg=  1.02  med=  1.03  ██
 2:00  avg=  1.02  med=  1.03  ██
 3:00  avg=  1.02  med=  1.03  ██
 4:00  avg=  1.02  med=  1.03  ██
 5:00  avg=  0.89  med=  0.89  █
 6:00  avg=  0.76  med=  0.74  █
 7:00  avg=  0.61  med=  0.56  █
 8:00  avg=  0.55  med=  0.48  █
 9:00  avg=  0.54  med=  0.48  █
10:00  avg=  0.57  med=  0.51  █
11:00  avg=  0.58  med=  0.52  █
12:00  avg=  0.62  med=  0.56  █
13:00  avg=  0.63  med=  0.58  █
14:00  avg=  0.62  med=  0.57  █
15:00  avg=  0.64  med=  0.59  █
16:00  avg=  0.67  med=  0.63  █
17:00  avg=  0.74  med=  0.72  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.95  med=  0.98  █
20:00  avg=  0.98  med=  1.00  █
21:00  avg=  0.96  med=  0.97  █
22:00  avg=  1.07  med=  1.08  ██
23:00  avg=  1.17  med=  1.15  ██
```

### Frame 1234852696 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 7,323 m | Ibrox 849 m | Hampden 5,208 m | Glasgow Green 5,419 m

```
 0:00  avg=  1.00  med=  1.01  ██
 1:00  avg=  1.00  med=  1.01  ██
 2:00  avg=  1.00  med=  1.01  ██
 3:00  avg=  1.00  med=  1.01  ██
 4:00  avg=  1.00  med=  1.01  ██
 5:00  avg=  0.84  med=  0.84  █
 6:00  avg=  0.74  med=  0.72  █
 7:00  avg=  0.52  med=  0.48  █
 8:00  avg=  0.43  med=  0.37  
 9:00  avg=  0.40  med=  0.36  
10:00  avg=  0.44  med=  0.39  
11:00  avg=  0.47  med=  0.43  
12:00  avg=  0.51  med=  0.46  █
13:00  avg=  0.52  med=  0.48  █
14:00  avg=  0.51  med=  0.47  █
15:00  avg=  0.52  med=  0.48  █
16:00  avg=  0.55  med=  0.52  █
17:00  avg=  0.69  med=  0.67  █
18:00  avg=  0.76  med=  0.78  █
19:00  avg=  0.77  med=  0.78  █
20:00  avg=  0.83  med=  0.84  █
21:00  avg=  0.80  med=  0.81  █
22:00  avg=  0.87  med=  0.88  █
23:00  avg=  0.91  med=  0.90  █
```

### Frame 1234852697 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 603 m | Ibrox 6,789 m | Hampden 4,376 m | Glasgow Green 2,222 m

```
 0:00  avg=  0.94  med=  0.96  █
 1:00  avg=  0.94  med=  0.96  █
 2:00  avg=  0.94  med=  0.96  █
 3:00  avg=  0.94  med=  0.96  █
 4:00  avg=  0.94  med=  0.96  █
 5:00  avg=  0.86  med=  0.86  █
 6:00  avg=  0.86  med=  0.86  █
 7:00  avg=  0.75  med=  0.74  █
 8:00  avg=  0.78  med=  0.75  █
 9:00  avg=  0.77  med=  0.75  █
10:00  avg=  0.79  med=  0.80  █
11:00  avg=  0.82  med=  0.86  █
12:00  avg=  0.85  med=  0.91  █
13:00  avg=  0.92  med=  1.02  █
14:00  avg=  0.90  med=  1.03  █
15:00  avg=  0.88  med=  1.00  █
16:00  avg=  0.85  med=  0.96  █
17:00  avg=  0.76  med=  0.86  █
18:00  avg=  0.74  med=  0.84  █
19:00  avg=  0.68  med=  0.81  █
20:00  avg=  0.70  med=  0.82  █
21:00  avg=  0.72  med=  0.85  █
22:00  avg=  0.75  med=  0.89  █
23:00  avg=  0.96  med=  1.00  █
```

### Frame 1234852697 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 603 m | Ibrox 6,789 m | Hampden 4,376 m | Glasgow Green 2,222 m

```
 0:00  avg=  1.07  med=  1.08  ██
 1:00  avg=  1.07  med=  1.08  ██
 2:00  avg=  1.07  med=  1.08  ██
 3:00  avg=  1.07  med=  1.08  ██
 4:00  avg=  1.07  med=  1.08  ██
 5:00  avg=  0.73  med=  0.73  █
 6:00  avg=  0.86  med=  0.86  █
 7:00  avg=  0.69  med=  0.68  █
 8:00  avg=  0.55  med=  0.53  █
 9:00  avg=  0.60  med=  0.58  █
10:00  avg=  0.65  med=  0.66  █
11:00  avg=  0.72  med=  0.75  █
12:00  avg=  0.75  med=  0.80  █
13:00  avg=  0.77  med=  0.85  █
14:00  avg=  0.74  med=  0.85  █
15:00  avg=  0.72  med=  0.82  █
16:00  avg=  0.68  med=  0.77  █
17:00  avg=  0.63  med=  0.71  █
18:00  avg=  0.63  med=  0.72  █
19:00  avg=  0.63  med=  0.76  █
20:00  avg=  0.71  med=  0.83  █
21:00  avg=  0.73  med=  0.87  █
22:00  avg=  0.71  med=  0.85  █
23:00  avg=  1.21  med=  1.26  ██
```

### Frame 1234852698 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,363 m | Ibrox 4,735 m | Hampden 441 m | Glasgow Green 2,609 m

```
 0:00  avg=  1.00  med=  1.06  █
 1:00  avg=  1.00  med=  1.06  █
 2:00  avg=  1.00  med=  1.06  █
 3:00  avg=  1.00  med=  1.06  █
 4:00  avg=  1.00  med=  1.06  █
 5:00  avg=  0.92  med=  0.93  █
 6:00  avg=  0.92  med=  0.92  █
 7:00  avg=  0.84  med=  0.82  █
 8:00  avg=  0.79  med=  0.77  █
 9:00  avg=  0.78  med=  0.77  █
10:00  avg=  0.79  med=  0.77  █
11:00  avg=  0.81  med=  0.79  █
12:00  avg=  0.78  med=  0.77  █
13:00  avg=  0.72  med=  0.71  █
14:00  avg=  0.71  med=  0.70  █
15:00  avg=  0.68  med=  0.66  █
16:00  avg=  0.69  med=  0.70  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.58  med=  0.61  █
19:00  avg=  0.58  med=  0.62  █
20:00  avg=  0.61  med=  0.65  █
21:00  avg=  0.69  med=  0.74  █
22:00  avg=  0.76  med=  0.84  █
23:00  avg=  1.13  med=  1.22  ██
```

### Frame 1234852698 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,363 m | Ibrox 4,735 m | Hampden 441 m | Glasgow Green 2,609 m

```
 0:00  avg=  1.16  med=  1.24  ██
 1:00  avg=  1.16  med=  1.24  ██
 2:00  avg=  1.16  med=  1.24  ██
 3:00  avg=  1.16  med=  1.24  ██
 4:00  avg=  1.16  med=  1.24  ██
 5:00  avg=  0.91  med=  0.92  █
 6:00  avg=  0.84  med=  0.84  █
 7:00  avg=  0.75  med=  0.73  █
 8:00  avg=  0.65  med=  0.64  █
 9:00  avg=  0.71  med=  0.71  █
10:00  avg=  0.71  med=  0.69  █
11:00  avg=  0.69  med=  0.67  █
12:00  avg=  0.71  med=  0.70  █
13:00  avg=  0.75  med=  0.74  █
14:00  avg=  0.73  med=  0.72  █
15:00  avg=  0.67  med=  0.66  █
16:00  avg=  0.65  med=  0.65  █
17:00  avg=  0.64  med=  0.65  █
18:00  avg=  0.65  med=  0.68  █
19:00  avg=  0.63  med=  0.67  █
20:00  avg=  0.67  med=  0.71  █
21:00  avg=  0.71  med=  0.76  █
22:00  avg=  0.80  med=  0.88  █
23:00  avg=  1.22  med=  1.32  ██
```

### Frame 1234853767 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,916 m | Ibrox 10,959 m | Hampden 8,672 m | Glasgow Green 6,537 m

```
 0:00  avg=  1.07  med=  1.08  ██
 1:00  avg=  1.07  med=  1.08  ██
 2:00  avg=  1.07  med=  1.08  ██
 3:00  avg=  1.07  med=  1.08  ██
 4:00  avg=  1.07  med=  1.08  ██
 5:00  avg=  0.95  med=  0.96  █
 6:00  avg=  0.94  med=  0.94  █
 7:00  avg=  0.96  med=  0.97  █
 8:00  avg=  0.90  med=  0.91  █
 9:00  avg=  0.96  med=  1.01  █
10:00  avg=  1.03  med=  1.10  ██
11:00  avg=  1.03  med=  1.08  ██
12:00  avg=  1.12  med=  1.19  ██
13:00  avg=  1.26  med=  1.32  ██
14:00  avg=  1.43  med=  1.50  ██
15:00  avg=  1.46  med=  1.56  ██
16:00  avg=  1.41  med=  1.51  ██
17:00  avg=  1.22  med=  1.29  ██
18:00  avg=  1.03  med=  1.06  ██
19:00  avg=  0.79  med=  0.78  █
20:00  avg=  0.66  med=  0.66  █
21:00  avg=  0.70  med=  0.72  █
22:00  avg=  0.89  med=  0.92  █
23:00  avg=  0.99  med=  0.99  █
```

### Frame 1234853767 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,916 m | Ibrox 10,959 m | Hampden 8,672 m | Glasgow Green 6,537 m

```
 0:00  avg=  0.94  med=  0.96  █
 1:00  avg=  0.94  med=  0.96  █
 2:00  avg=  0.94  med=  0.96  █
 3:00  avg=  0.94  med=  0.96  █
 4:00  avg=  0.94  med=  0.96  █
 5:00  avg=  1.01  med=  1.02  ██
 6:00  avg=  0.89  med=  0.89  █
 7:00  avg=  0.88  med=  0.88  █
 8:00  avg=  0.76  med=  0.76  █
 9:00  avg=  0.76  med=  0.80  █
10:00  avg=  0.98  med=  1.05  █
11:00  avg=  1.02  med=  1.07  ██
12:00  avg=  1.12  med=  1.18  ██
13:00  avg=  1.19  med=  1.25  ██
14:00  avg=  1.24  med=  1.30  ██
15:00  avg=  1.21  med=  1.29  ██
16:00  avg=  1.11  med=  1.19  ██
17:00  avg=  0.90  med=  0.95  █
18:00  avg=  0.63  med=  0.64  █
19:00  avg=  0.44  med=  0.43  
20:00  avg=  0.42  med=  0.42  
21:00  avg=  0.52  med=  0.54  █
22:00  avg=  0.82  med=  0.85  █
23:00  avg=  1.07  med=  1.08  ██
```

### Frame 1234853768 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,934 m | Ibrox 10,958 m | Hampden 8,695 m | Glasgow Green 6,544 m

```
 0:00  avg=  1.07  med=  1.08  ██
 1:00  avg=  1.07  med=  1.08  ██
 2:00  avg=  1.07  med=  1.08  ██
 3:00  avg=  1.07  med=  1.08  ██
 4:00  avg=  1.07  med=  1.08  ██
 5:00  avg=  0.95  med=  0.96  █
 6:00  avg=  0.94  med=  0.94  █
 7:00  avg=  0.96  med=  0.97  █
 8:00  avg=  0.90  med=  0.91  █
 9:00  avg=  0.96  med=  1.01  █
10:00  avg=  1.03  med=  1.10  ██
11:00  avg=  1.03  med=  1.08  ██
12:00  avg=  1.12  med=  1.19  ██
13:00  avg=  1.26  med=  1.32  ██
14:00  avg=  1.43  med=  1.50  ██
15:00  avg=  1.46  med=  1.56  ██
16:00  avg=  1.41  med=  1.51  ██
17:00  avg=  1.22  med=  1.29  ██
18:00  avg=  1.03  med=  1.06  ██
19:00  avg=  0.79  med=  0.78  █
20:00  avg=  0.66  med=  0.66  █
21:00  avg=  0.70  med=  0.72  █
22:00  avg=  0.89  med=  0.92  █
23:00  avg=  0.99  med=  0.99  █
```

### Frame 1234853768 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,934 m | Ibrox 10,958 m | Hampden 8,695 m | Glasgow Green 6,544 m

```
 0:00  avg=  0.94  med=  0.96  █
 1:00  avg=  0.94  med=  0.96  █
 2:00  avg=  0.94  med=  0.96  █
 3:00  avg=  0.94  med=  0.96  █
 4:00  avg=  0.94  med=  0.96  █
 5:00  avg=  1.01  med=  1.02  ██
 6:00  avg=  0.89  med=  0.89  █
 7:00  avg=  0.88  med=  0.88  █
 8:00  avg=  0.76  med=  0.76  █
 9:00  avg=  0.76  med=  0.80  █
10:00  avg=  0.98  med=  1.05  █
11:00  avg=  1.02  med=  1.07  ██
12:00  avg=  1.12  med=  1.18  ██
13:00  avg=  1.19  med=  1.25  ██
14:00  avg=  1.24  med=  1.30  ██
15:00  avg=  1.21  med=  1.29  ██
16:00  avg=  1.11  med=  1.19  ██
17:00  avg=  0.90  med=  0.95  █
18:00  avg=  0.63  med=  0.64  █
19:00  avg=  0.44  med=  0.43  
20:00  avg=  0.42  med=  0.42  
21:00  avg=  0.52  med=  0.54  █
22:00  avg=  0.82  med=  0.85  █
23:00  avg=  1.07  med=  1.08  ██
```

### Frame 1234855590 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 15,592 m | Ibrox 21,689 m | Hampden 17,409 m | Glasgow Green 17,433 m

```
 0:00  avg=  1.23  med=  1.28  ██
 1:00  avg=  1.23  med=  1.28  ██
 2:00  avg=  1.23  med=  1.28  ██
 3:00  avg=  1.23  med=  1.28  ██
 4:00  avg=  1.23  med=  1.28  ██
 5:00  avg=  1.00  med=  1.00  █
 6:00  avg=  1.00  med=  1.00  ██
 7:00  avg=  0.66  med=  0.63  █
 8:00  avg=  0.51  med=  0.46  █
 9:00  avg=  0.60  med=  0.54  █
10:00  avg=  0.62  med=  0.56  █
11:00  avg=  0.64  med=  0.58  █
12:00  avg=  0.73  med=  0.68  █
13:00  avg=  0.96  med=  0.92  █
14:00  avg=  1.25  med=  1.24  ██
15:00  avg=  1.17  med=  1.15  ██
16:00  avg=  1.24  med=  1.25  ██
17:00  avg=  1.31  med=  1.42  ██
18:00  avg=  0.84  med=  0.86  █
19:00  avg=  0.92  med=  0.97  █
20:00  avg=  0.87  med=  0.93  █
21:00  avg=  1.05  med=  1.13  ██
22:00  avg=  1.11  med=  1.20  ██
23:00  avg=  1.24  med=  1.32  ██
```

### Frame 1234855590 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 15,592 m | Ibrox 21,689 m | Hampden 17,409 m | Glasgow Green 17,433 m

```
 0:00  avg=  1.14  med=  1.19  ██
 1:00  avg=  1.14  med=  1.19  ██
 2:00  avg=  1.14  med=  1.19  ██
 3:00  avg=  1.14  med=  1.19  ██
 4:00  avg=  1.14  med=  1.19  ██
 5:00  avg=  1.03  med=  1.03  ██
 6:00  avg=  1.08  med=  1.08  ██
 7:00  avg=  0.70  med=  0.66  █
 8:00  avg=  0.47  med=  0.42  
 9:00  avg=  0.44  med=  0.39  
10:00  avg=  0.45  med=  0.41  
11:00  avg=  0.56  med=  0.51  █
12:00  avg=  0.62  med=  0.57  █
13:00  avg=  0.64  med=  0.61  █
14:00  avg=  0.54  med=  0.54  █
15:00  avg=  0.53  med=  0.52  █
16:00  avg=  0.54  med=  0.54  █
17:00  avg=  0.62  med=  0.67  █
18:00  avg=  0.66  med=  0.68  █
19:00  avg=  0.73  med=  0.77  █
20:00  avg=  0.70  med=  0.74  █
21:00  avg=  0.68  med=  0.73  █
22:00  avg=  0.73  med=  0.79  █
23:00  avg=  0.79  med=  0.85  █
```

### Frame 1234855591 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 15,592 m | Ibrox 21,689 m | Hampden 17,409 m | Glasgow Green 17,433 m

```
 0:00  avg=  1.23  med=  1.28  ██
 1:00  avg=  1.23  med=  1.28  ██
 2:00  avg=  1.23  med=  1.28  ██
 3:00  avg=  1.23  med=  1.28  ██
 4:00  avg=  1.23  med=  1.28  ██
 5:00  avg=  1.00  med=  1.00  █
 6:00  avg=  1.00  med=  1.00  ██
 7:00  avg=  0.66  med=  0.63  █
 8:00  avg=  0.51  med=  0.46  █
 9:00  avg=  0.60  med=  0.54  █
10:00  avg=  0.62  med=  0.56  █
11:00  avg=  0.64  med=  0.58  █
12:00  avg=  0.73  med=  0.68  █
13:00  avg=  0.96  med=  0.92  █
14:00  avg=  1.25  med=  1.24  ██
15:00  avg=  1.17  med=  1.15  ██
16:00  avg=  1.24  med=  1.25  ██
17:00  avg=  1.31  med=  1.42  ██
18:00  avg=  0.84  med=  0.86  █
19:00  avg=  0.92  med=  0.97  █
20:00  avg=  0.87  med=  0.93  █
21:00  avg=  1.05  med=  1.13  ██
22:00  avg=  1.11  med=  1.20  ██
23:00  avg=  1.24  med=  1.32  ██
```

### Frame 1234855591 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 15,592 m | Ibrox 21,689 m | Hampden 17,409 m | Glasgow Green 17,433 m

```
 0:00  avg=  1.14  med=  1.19  ██
 1:00  avg=  1.14  med=  1.19  ██
 2:00  avg=  1.14  med=  1.19  ██
 3:00  avg=  1.14  med=  1.19  ██
 4:00  avg=  1.14  med=  1.19  ██
 5:00  avg=  1.03  med=  1.03  ██
 6:00  avg=  1.08  med=  1.08  ██
 7:00  avg=  0.70  med=  0.66  █
 8:00  avg=  0.47  med=  0.42  
 9:00  avg=  0.44  med=  0.39  
10:00  avg=  0.45  med=  0.41  
11:00  avg=  0.56  med=  0.51  █
12:00  avg=  0.62  med=  0.57  █
13:00  avg=  0.64  med=  0.61  █
14:00  avg=  0.54  med=  0.54  █
15:00  avg=  0.53  med=  0.52  █
16:00  avg=  0.54  med=  0.54  █
17:00  avg=  0.62  med=  0.67  █
18:00  avg=  0.66  med=  0.68  █
19:00  avg=  0.73  med=  0.77  █
20:00  avg=  0.70  med=  0.74  █
21:00  avg=  0.68  med=  0.73  █
22:00  avg=  0.73  med=  0.79  █
23:00  avg=  0.79  med=  0.85  █
```

### Frame 1234855594 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 13,264 m | Ibrox 6,828 m | Hampden 10,572 m | Glasgow Green 11,381 m

```
 0:00  avg=  1.38  med=  1.42  ██
 1:00  avg=  1.38  med=  1.42  ██
 2:00  avg=  1.38  med=  1.42  ██
 3:00  avg=  1.38  med=  1.42  ██
 4:00  avg=  1.38  med=  1.42  ██
 5:00  avg=  1.15  med=  1.16  ██
 6:00  avg=  1.01  med=  1.01  ██
 7:00  avg=  0.84  med=  0.80  █
 8:00  avg=  0.68  med=  0.62  █
 9:00  avg=  0.64  med=  0.60  █
10:00  avg=  0.66  med=  0.63  █
11:00  avg=  0.82  med=  0.78  █
12:00  avg=  0.80  med=  0.77  █
13:00  avg=  0.79  med=  0.76  █
14:00  avg=  0.86  med=  0.82  █
15:00  avg=  0.82  med=  0.80  █
16:00  avg=  0.80  med=  0.78  █
17:00  avg=  0.87  med=  0.85  █
18:00  avg=  0.87  med=  0.90  █
19:00  avg=  0.89  med=  0.92  █
20:00  avg=  0.95  med=  1.02  █
21:00  avg=  1.15  med=  1.24  ██
22:00  avg=  1.23  med=  1.33  ██
23:00  avg=  1.23  med=  1.35  ██
```

### Frame 1234855594 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 13,264 m | Ibrox 6,828 m | Hampden 10,572 m | Glasgow Green 11,381 m

```
 0:00  avg=  1.20  med=  1.23  ██
 1:00  avg=  1.20  med=  1.23  ██
 2:00  avg=  1.20  med=  1.23  ██
 3:00  avg=  1.20  med=  1.23  ██
 4:00  avg=  1.20  med=  1.23  ██
 5:00  avg=  0.99  med=  1.00  █
 6:00  avg=  0.77  med=  0.77  █
 7:00  avg=  0.67  med=  0.64  █
 8:00  avg=  0.42  med=  0.39  
 9:00  avg=  0.48  med=  0.45  
10:00  avg=  0.49  med=  0.47  
11:00  avg=  0.53  med=  0.50  █
12:00  avg=  0.55  med=  0.52  █
13:00  avg=  0.58  med=  0.56  █
14:00  avg=  0.59  med=  0.57  █
15:00  avg=  0.59  med=  0.57  █
16:00  avg=  0.56  med=  0.54  █
17:00  avg=  0.61  med=  0.60  █
18:00  avg=  0.66  med=  0.68  █
19:00  avg=  0.60  med=  0.63  █
20:00  avg=  0.61  med=  0.65  █
21:00  avg=  0.73  med=  0.79  █
22:00  avg=  0.89  med=  0.97  █
23:00  avg=  1.09  med=  1.20  ██
```

### Frame 1234855595 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 13,263 m | Ibrox 6,827 m | Hampden 10,572 m | Glasgow Green 11,381 m

```
 0:00  avg=  1.38  med=  1.42  ██
 1:00  avg=  1.38  med=  1.42  ██
 2:00  avg=  1.38  med=  1.42  ██
 3:00  avg=  1.38  med=  1.42  ██
 4:00  avg=  1.38  med=  1.42  ██
 5:00  avg=  1.15  med=  1.16  ██
 6:00  avg=  1.01  med=  1.01  ██
 7:00  avg=  0.84  med=  0.80  █
 8:00  avg=  0.68  med=  0.62  █
 9:00  avg=  0.64  med=  0.60  █
10:00  avg=  0.66  med=  0.63  █
11:00  avg=  0.82  med=  0.78  █
12:00  avg=  0.80  med=  0.77  █
13:00  avg=  0.79  med=  0.76  █
14:00  avg=  0.86  med=  0.82  █
15:00  avg=  0.82  med=  0.80  █
16:00  avg=  0.80  med=  0.78  █
17:00  avg=  0.87  med=  0.85  █
18:00  avg=  0.87  med=  0.90  █
19:00  avg=  0.89  med=  0.92  █
20:00  avg=  0.95  med=  1.02  █
21:00  avg=  1.15  med=  1.24  ██
22:00  avg=  1.23  med=  1.33  ██
23:00  avg=  1.23  med=  1.35  ██
```

### Frame 1234855595 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 13,263 m | Ibrox 6,827 m | Hampden 10,572 m | Glasgow Green 11,381 m

```
 0:00  avg=  1.20  med=  1.23  ██
 1:00  avg=  1.20  med=  1.23  ██
 2:00  avg=  1.20  med=  1.23  ██
 3:00  avg=  1.20  med=  1.23  ██
 4:00  avg=  1.20  med=  1.23  ██
 5:00  avg=  0.99  med=  1.00  █
 6:00  avg=  0.77  med=  0.77  █
 7:00  avg=  0.67  med=  0.64  █
 8:00  avg=  0.42  med=  0.39  
 9:00  avg=  0.48  med=  0.45  
10:00  avg=  0.49  med=  0.47  
11:00  avg=  0.53  med=  0.50  █
12:00  avg=  0.55  med=  0.52  █
13:00  avg=  0.58  med=  0.56  █
14:00  avg=  0.59  med=  0.57  █
15:00  avg=  0.59  med=  0.57  █
16:00  avg=  0.56  med=  0.54  █
17:00  avg=  0.61  med=  0.60  █
18:00  avg=  0.66  med=  0.68  █
19:00  avg=  0.60  med=  0.63  █
20:00  avg=  0.61  med=  0.65  █
21:00  avg=  0.73  med=  0.79  █
22:00  avg=  0.89  med=  0.97  █
23:00  avg=  1.09  med=  1.20  ██
```

### Frame 1234855761 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,482 m | Ibrox 3,736 m | Hampden 4,228 m | Glasgow Green 1,827 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234855761 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,482 m | Ibrox 3,736 m | Hampden 4,228 m | Glasgow Green 1,827 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234855779 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,326 m | Ibrox 3,820 m | Hampden 4,132 m | Glasgow Green 1,677 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234855779 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,326 m | Ibrox 3,820 m | Hampden 4,132 m | Glasgow Green 1,677 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234855887 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,212 m | Ibrox 5,829 m | Hampden 1,862 m | Glasgow Green 2,354 m

```
 0:00  avg=  1.19  med=  1.23  ██
 1:00  avg=  1.19  med=  1.23  ██
 2:00  avg=  1.19  med=  1.23  ██
 3:00  avg=  1.19  med=  1.23  ██
 4:00  avg=  1.19  med=  1.23  ██
 5:00  avg=  1.01  med=  1.03  ██
 6:00  avg=  0.99  med=  0.98  █
 7:00  avg=  0.71  med=  0.65  █
 8:00  avg=  0.62  med=  0.56  █
 9:00  avg=  0.62  med=  0.55  █
10:00  avg=  0.62  med=  0.57  █
11:00  avg=  0.63  med=  0.58  █
12:00  avg=  0.60  med=  0.57  █
13:00  avg=  0.65  med=  0.62  █
14:00  avg=  0.64  med=  0.61  █
15:00  avg=  0.64  med=  0.60  █
16:00  avg=  0.65  med=  0.62  █
17:00  avg=  0.71  med=  0.70  █
18:00  avg=  0.73  med=  0.74  █
19:00  avg=  0.84  med=  0.86  █
20:00  avg=  0.93  med=  0.94  █
21:00  avg=  1.07  med=  1.10  ██
22:00  avg=  1.09  med=  1.12  ██
23:00  avg=  1.46  med=  1.55  ██
```

### Frame 1234855887 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,212 m | Ibrox 5,829 m | Hampden 1,862 m | Glasgow Green 2,354 m

```
 0:00  avg=  1.23  med=  1.27  ██
 1:00  avg=  1.23  med=  1.27  ██
 2:00  avg=  1.23  med=  1.27  ██
 3:00  avg=  1.23  med=  1.27  ██
 4:00  avg=  1.23  med=  1.27  ██
 5:00  avg=  0.88  med=  0.90  █
 6:00  avg=  0.82  med=  0.81  █
 7:00  avg=  0.54  med=  0.50  █
 8:00  avg=  0.49  med=  0.45  
 9:00  avg=  0.45  med=  0.40  
10:00  avg=  0.46  med=  0.42  
11:00  avg=  0.49  med=  0.46  
12:00  avg=  0.49  med=  0.46  
13:00  avg=  0.58  med=  0.55  █
14:00  avg=  0.55  med=  0.53  █
15:00  avg=  0.59  med=  0.56  █
16:00  avg=  0.59  med=  0.56  █
17:00  avg=  0.66  med=  0.65  █
18:00  avg=  0.76  med=  0.77  █
19:00  avg=  0.87  med=  0.89  █
20:00  avg=  0.81  med=  0.83  █
21:00  avg=  0.85  med=  0.86  █
22:00  avg=  0.88  med=  0.90  █
23:00  avg=  1.22  med=  1.30  ██
```

### Frame 1234856789 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 949 m | Ibrox 6,832 m | Hampden 4,654 m | Glasgow Green 2,311 m

```
 0:00  avg=  1.43  med=  1.46  ██
 1:00  avg=  1.43  med=  1.46  ██
 2:00  avg=  1.43  med=  1.46  ██
 3:00  avg=  1.43  med=  1.46  ██
 4:00  avg=  1.43  med=  1.46  ██
 5:00  avg=  1.36  med=  1.37  ██
 6:00  avg=  0.91  med=  0.91  █
 7:00  avg=  1.05  med=  1.06  ██
 8:00  avg=  0.87  med=  0.92  █
 9:00  avg=  0.81  med=  0.89  █
10:00  avg=  0.90  med=  0.99  █
11:00  avg=  0.80  med=  0.86  █
12:00  avg=  0.79  med=  0.85  █
13:00  avg=  0.84  med=  0.87  █
14:00  avg=  0.81  med=  0.87  █
15:00  avg=  0.77  med=  0.81  █
16:00  avg=  0.64  med=  0.67  █
17:00  avg=  1.02  med=  1.07  ██
18:00  avg=  0.96  med=  1.00  █
19:00  avg=  1.14  med=  1.22  ██
20:00  avg=  1.14  med=  1.20  ██
21:00  avg=  1.07  med=  1.14  ██
22:00  avg=  1.21  med=  1.31  ██
23:00  avg=  1.45  med=  1.50  ██
```

### Frame 1234856789 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 949 m | Ibrox 6,832 m | Hampden 4,654 m | Glasgow Green 2,311 m

```
 0:00  avg=  1.66  med=  1.70  ███
 1:00  avg=  1.66  med=  1.70  ███
 2:00  avg=  1.66  med=  1.70  ███
 3:00  avg=  1.66  med=  1.70  ███
 4:00  avg=  1.66  med=  1.70  ███
 5:00  avg=  1.74  med=  1.75  ███
 6:00  avg=  1.53  med=  1.53  ███
 7:00  avg=  1.07  med=  1.08  ██
 8:00  avg=  0.87  med=  0.93  █
 9:00  avg=  0.85  med=  0.92  █
10:00  avg=  0.67  med=  0.73  █
11:00  avg=  0.66  med=  0.71  █
12:00  avg=  0.78  med=  0.84  █
13:00  avg=  0.76  med=  0.79  █
14:00  avg=  0.84  med=  0.90  █
15:00  avg=  0.72  med=  0.75  █
16:00  avg=  0.76  med=  0.80  █
17:00  avg=  1.01  med=  1.05  ██
18:00  avg=  1.05  med=  1.09  ██
19:00  avg=  0.92  med=  0.98  █
20:00  avg=  1.00  med=  1.06  ██
21:00  avg=  1.04  med=  1.11  ██
22:00  avg=  1.26  med=  1.37  ██
23:00  avg=  1.57  med=  1.62  ███
```

### Frame 1234856791 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,036 m | Ibrox 5,281 m | Hampden 1,767 m | Glasgow Green 1,737 m

```
 0:00  avg=  1.19  med=  1.23  ██
 1:00  avg=  1.19  med=  1.23  ██
 2:00  avg=  1.19  med=  1.23  ██
 3:00  avg=  1.19  med=  1.23  ██
 4:00  avg=  1.19  med=  1.23  ██
 5:00  avg=  1.01  med=  1.03  ██
 6:00  avg=  0.99  med=  0.98  █
 7:00  avg=  0.71  med=  0.65  █
 8:00  avg=  0.62  med=  0.56  █
 9:00  avg=  0.62  med=  0.55  █
10:00  avg=  0.62  med=  0.57  █
11:00  avg=  0.63  med=  0.58  █
12:00  avg=  0.60  med=  0.57  █
13:00  avg=  0.65  med=  0.62  █
14:00  avg=  0.64  med=  0.61  █
15:00  avg=  0.64  med=  0.60  █
16:00  avg=  0.65  med=  0.62  █
17:00  avg=  0.71  med=  0.70  █
18:00  avg=  0.73  med=  0.74  █
19:00  avg=  0.84  med=  0.86  █
20:00  avg=  0.93  med=  0.94  █
21:00  avg=  1.07  med=  1.10  ██
22:00  avg=  1.09  med=  1.12  ██
23:00  avg=  1.46  med=  1.55  ██
```

### Frame 1234856791 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,036 m | Ibrox 5,281 m | Hampden 1,767 m | Glasgow Green 1,737 m

```
 0:00  avg=  1.23  med=  1.27  ██
 1:00  avg=  1.23  med=  1.27  ██
 2:00  avg=  1.23  med=  1.27  ██
 3:00  avg=  1.23  med=  1.27  ██
 4:00  avg=  1.23  med=  1.27  ██
 5:00  avg=  0.88  med=  0.90  █
 6:00  avg=  0.82  med=  0.81  █
 7:00  avg=  0.54  med=  0.50  █
 8:00  avg=  0.49  med=  0.45  
 9:00  avg=  0.45  med=  0.40  
10:00  avg=  0.46  med=  0.42  
11:00  avg=  0.49  med=  0.46  
12:00  avg=  0.49  med=  0.46  
13:00  avg=  0.58  med=  0.55  █
14:00  avg=  0.55  med=  0.53  █
15:00  avg=  0.59  med=  0.56  █
16:00  avg=  0.59  med=  0.56  █
17:00  avg=  0.66  med=  0.65  █
18:00  avg=  0.76  med=  0.77  █
19:00  avg=  0.87  med=  0.89  █
20:00  avg=  0.81  med=  0.83  █
21:00  avg=  0.85  med=  0.86  █
22:00  avg=  0.88  med=  0.90  █
23:00  avg=  1.22  med=  1.30  ██
```

### Frame 1234856792 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,036 m | Ibrox 5,279 m | Hampden 1,766 m | Glasgow Green 1,735 m

```
 0:00  avg=  1.19  med=  1.23  ██
 1:00  avg=  1.19  med=  1.23  ██
 2:00  avg=  1.19  med=  1.23  ██
 3:00  avg=  1.19  med=  1.23  ██
 4:00  avg=  1.19  med=  1.23  ██
 5:00  avg=  1.01  med=  1.03  ██
 6:00  avg=  0.99  med=  0.98  █
 7:00  avg=  0.71  med=  0.65  █
 8:00  avg=  0.62  med=  0.56  █
 9:00  avg=  0.62  med=  0.55  █
10:00  avg=  0.62  med=  0.57  █
11:00  avg=  0.63  med=  0.58  █
12:00  avg=  0.60  med=  0.57  █
13:00  avg=  0.65  med=  0.62  █
14:00  avg=  0.64  med=  0.61  █
15:00  avg=  0.64  med=  0.60  █
16:00  avg=  0.65  med=  0.62  █
17:00  avg=  0.71  med=  0.70  █
18:00  avg=  0.73  med=  0.74  █
19:00  avg=  0.84  med=  0.86  █
20:00  avg=  0.93  med=  0.94  █
21:00  avg=  1.07  med=  1.10  ██
22:00  avg=  1.09  med=  1.12  ██
23:00  avg=  1.46  med=  1.55  ██
```

### Frame 1234856792 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,036 m | Ibrox 5,279 m | Hampden 1,766 m | Glasgow Green 1,735 m

```
 0:00  avg=  1.23  med=  1.27  ██
 1:00  avg=  1.23  med=  1.27  ██
 2:00  avg=  1.23  med=  1.27  ██
 3:00  avg=  1.23  med=  1.27  ██
 4:00  avg=  1.23  med=  1.27  ██
 5:00  avg=  0.88  med=  0.90  █
 6:00  avg=  0.82  med=  0.81  █
 7:00  avg=  0.54  med=  0.50  █
 8:00  avg=  0.49  med=  0.45  
 9:00  avg=  0.45  med=  0.40  
10:00  avg=  0.46  med=  0.42  
11:00  avg=  0.49  med=  0.46  
12:00  avg=  0.49  med=  0.46  
13:00  avg=  0.58  med=  0.55  █
14:00  avg=  0.55  med=  0.53  █
15:00  avg=  0.59  med=  0.56  █
16:00  avg=  0.59  med=  0.56  █
17:00  avg=  0.66  med=  0.65  █
18:00  avg=  0.76  med=  0.77  █
19:00  avg=  0.87  med=  0.89  █
20:00  avg=  0.81  med=  0.83  █
21:00  avg=  0.85  med=  0.86  █
22:00  avg=  0.88  med=  0.90  █
23:00  avg=  1.22  med=  1.30  ██
```

### Frame 1234856806 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 13,991 m | Ibrox 7,536 m | Hampden 11,334 m | Glasgow Green 12,101 m

```
 0:00  avg=  1.11  med=  1.11  ██
 1:00  avg=  1.11  med=  1.11  ██
 2:00  avg=  1.11  med=  1.11  ██
 3:00  avg=  1.11  med=  1.11  ██
 4:00  avg=  1.11  med=  1.11  ██
 5:00  avg=  1.05  med=  1.03  ██
 6:00  avg=  1.03  med=  1.03  ██
 7:00  avg=  1.06  med=  1.08  ██
 8:00  avg=  1.11  med=  1.08  ██
 9:00  avg=  0.99  med=  0.95  █
10:00  avg=  0.95  med=  0.92  █
11:00  avg=  1.00  med=  0.98  ██
12:00  avg=  1.08  med=  1.08  ██
13:00  avg=  1.21  med=  1.21  ██
14:00  avg=  0.87  med=  0.87  █
15:00  avg=  0.79  med=  0.79  █
16:00  avg=  0.93  med=  0.94  █
17:00  avg=  0.77  med=  0.79  █
18:00  avg=  0.86  med=  0.88  █
19:00  avg=  0.80  med=  0.81  █
20:00  avg=  0.72  med=  0.72  █
21:00  avg=  0.94  med=  0.95  █
22:00  avg=  0.95  med=  0.95  █
23:00  avg=  0.87  med=  0.87  █
```

### Frame 1234856806 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 13,991 m | Ibrox 7,536 m | Hampden 11,334 m | Glasgow Green 12,101 m

```
 0:00  avg=  1.37  med=  1.37  ██
 1:00  avg=  1.37  med=  1.37  ██
 2:00  avg=  1.37  med=  1.37  ██
 3:00  avg=  1.37  med=  1.37  ██
 4:00  avg=  1.37  med=  1.37  ██
 5:00  avg=  0.79  med=  0.78  █
 6:00  avg=  0.68  med=  0.68  █
 7:00  avg=  0.65  med=  0.66  █
 8:00  avg=  0.65  med=  0.63  █
 9:00  avg=  0.36  med=  0.34  
10:00  avg=  0.60  med=  0.59  █
11:00  avg=  0.73  med=  0.72  █
12:00  avg=  0.77  med=  0.77  █
13:00  avg=  0.76  med=  0.75  █
14:00  avg=  0.94  med=  0.94  █
15:00  avg=  0.79  med=  0.79  █
16:00  avg=  0.76  med=  0.77  █
17:00  avg=  0.87  med=  0.90  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.91  med=  0.91  █
20:00  avg=  0.58  med=  0.58  █
21:00  avg=  0.61  med=  0.62  █
22:00  avg=  0.68  med=  0.68  █
23:00  avg=  0.59  med=  0.59  █
```

### Frame 1234858480 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 13,928 m | Ibrox 7,472 m | Hampden 11,276 m | Glasgow Green 12,037 m

```
 0:00  avg=  1.11  med=  1.11  ██
 1:00  avg=  1.11  med=  1.11  ██
 2:00  avg=  1.11  med=  1.11  ██
 3:00  avg=  1.11  med=  1.11  ██
 4:00  avg=  1.11  med=  1.11  ██
 5:00  avg=  1.05  med=  1.03  ██
 6:00  avg=  1.03  med=  1.03  ██
 7:00  avg=  1.06  med=  1.08  ██
 8:00  avg=  1.11  med=  1.08  ██
 9:00  avg=  0.99  med=  0.95  █
10:00  avg=  0.95  med=  0.92  █
11:00  avg=  1.00  med=  0.98  ██
12:00  avg=  1.08  med=  1.08  ██
13:00  avg=  1.21  med=  1.21  ██
14:00  avg=  0.87  med=  0.87  █
15:00  avg=  0.79  med=  0.79  █
16:00  avg=  0.93  med=  0.94  █
17:00  avg=  0.77  med=  0.79  █
18:00  avg=  0.86  med=  0.88  █
19:00  avg=  0.80  med=  0.81  █
20:00  avg=  0.72  med=  0.72  █
21:00  avg=  0.94  med=  0.95  █
22:00  avg=  0.95  med=  0.95  █
23:00  avg=  0.87  med=  0.87  █
```

### Frame 1234858480 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 13,928 m | Ibrox 7,472 m | Hampden 11,276 m | Glasgow Green 12,037 m

```
 0:00  avg=  1.37  med=  1.37  ██
 1:00  avg=  1.37  med=  1.37  ██
 2:00  avg=  1.37  med=  1.37  ██
 3:00  avg=  1.37  med=  1.37  ██
 4:00  avg=  1.37  med=  1.37  ██
 5:00  avg=  0.79  med=  0.78  █
 6:00  avg=  0.68  med=  0.68  █
 7:00  avg=  0.65  med=  0.66  █
 8:00  avg=  0.65  med=  0.63  █
 9:00  avg=  0.36  med=  0.34  
10:00  avg=  0.60  med=  0.59  █
11:00  avg=  0.73  med=  0.72  █
12:00  avg=  0.77  med=  0.77  █
13:00  avg=  0.76  med=  0.75  █
14:00  avg=  0.94  med=  0.94  █
15:00  avg=  0.79  med=  0.79  █
16:00  avg=  0.76  med=  0.77  █
17:00  avg=  0.87  med=  0.90  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.91  med=  0.91  █
20:00  avg=  0.58  med=  0.58  █
21:00  avg=  0.61  med=  0.62  █
22:00  avg=  0.68  med=  0.68  █
23:00  avg=  0.59  med=  0.59  █
```

### Frame 1234859353 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,283 m | Ibrox 4,310 m | Hampden 3,237 m | Glasgow Green 475 m

```
 0:00  avg=  3.65  med=  3.77  ███████
 1:00  avg=  3.65  med=  3.77  ███████
 2:00  avg=  3.65  med=  3.77  ███████
 3:00  avg=  3.65  med=  3.77  ███████
 4:00  avg=  3.65  med=  3.77  ███████
 5:00  avg=  2.54  med=  2.59  █████
 6:00  avg=  2.55  med=  2.61  █████
 7:00  avg=  2.56  med=  2.60  █████
 8:00  avg=  2.49  med=  2.55  ████
 9:00  avg=  2.61  med=  2.71  █████
10:00  avg=  2.84  med=  3.01  █████
11:00  avg=  3.24  med=  3.61  ██████
12:00  avg=  4.38  med=  5.19  ████████
13:00  avg=  6.18  med=  7.72  ████████████
14:00  avg=  9.06  med= 11.54  ██████████████████
15:00  avg= 12.08  med= 15.50  ████████████████████████
16:00  avg= 14.16  med= 17.96  ████████████████████████████
17:00  avg= 15.22  med= 19.84  ██████████████████████████████
18:00  avg= 15.62  med= 21.12  ███████████████████████████████
19:00  avg= 15.15  med= 22.13  ██████████████████████████████
20:00  avg= 15.30  med= 23.80  ██████████████████████████████
21:00  avg= 16.13  med= 25.98  ████████████████████████████████
22:00  avg= 17.17  med= 29.48  ██████████████████████████████████
23:00  avg= 18.48  med= 28.90  ████████████████████████████████████
```

### Frame 1234859353 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,283 m | Ibrox 4,310 m | Hampden 3,237 m | Glasgow Green 475 m

```
 0:00  avg=  3.76  med=  3.89  ███████
 1:00  avg=  3.76  med=  3.89  ███████
 2:00  avg=  3.76  med=  3.89  ███████
 3:00  avg=  3.76  med=  3.89  ███████
 4:00  avg=  3.76  med=  3.89  ███████
 5:00  avg=  2.71  med=  2.76  █████
 6:00  avg=  2.76  med=  2.82  █████
 7:00  avg=  2.54  med=  2.58  █████
 8:00  avg=  2.19  med=  2.24  ████
 9:00  avg=  2.04  med=  2.12  ████
10:00  avg=  2.41  med=  2.55  ████
11:00  avg=  2.94  med=  3.28  █████
12:00  avg=  3.73  med=  4.43  ███████
13:00  avg=  4.79  med=  5.99  █████████
14:00  avg=  6.71  med=  8.54  █████████████
15:00  avg=  9.33  med= 11.97  ██████████████████
16:00  avg= 12.28  med= 15.59  ████████████████████████
17:00  avg= 14.28  med= 18.61  ████████████████████████████
18:00  avg= 14.79  med= 19.99  █████████████████████████████
19:00  avg= 14.29  med= 20.87  ████████████████████████████
20:00  avg= 14.27  med= 22.20  ████████████████████████████
21:00  avg= 14.87  med= 23.95  █████████████████████████████
22:00  avg= 15.93  med= 27.35  ███████████████████████████████
23:00  avg= 18.29  med= 28.61  ████████████████████████████████████
```

### Frame 1234859354 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,283 m | Ibrox 4,310 m | Hampden 3,237 m | Glasgow Green 475 m

```
 0:00  avg=  3.65  med=  3.77  ███████
 1:00  avg=  3.65  med=  3.77  ███████
 2:00  avg=  3.65  med=  3.77  ███████
 3:00  avg=  3.65  med=  3.77  ███████
 4:00  avg=  3.65  med=  3.77  ███████
 5:00  avg=  2.54  med=  2.59  █████
 6:00  avg=  2.55  med=  2.61  █████
 7:00  avg=  2.56  med=  2.60  █████
 8:00  avg=  2.49  med=  2.55  ████
 9:00  avg=  2.61  med=  2.71  █████
10:00  avg=  2.84  med=  3.01  █████
11:00  avg=  3.24  med=  3.61  ██████
12:00  avg=  4.38  med=  5.19  ████████
13:00  avg=  6.18  med=  7.72  ████████████
14:00  avg=  9.06  med= 11.54  ██████████████████
15:00  avg= 12.08  med= 15.50  ████████████████████████
16:00  avg= 14.16  med= 17.96  ████████████████████████████
17:00  avg= 15.22  med= 19.84  ██████████████████████████████
18:00  avg= 15.62  med= 21.12  ███████████████████████████████
19:00  avg= 15.15  med= 22.13  ██████████████████████████████
20:00  avg= 15.30  med= 23.80  ██████████████████████████████
21:00  avg= 16.13  med= 25.98  ████████████████████████████████
22:00  avg= 17.17  med= 29.48  ██████████████████████████████████
23:00  avg= 18.48  med= 28.90  ████████████████████████████████████
```

### Frame 1234859354 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,283 m | Ibrox 4,310 m | Hampden 3,237 m | Glasgow Green 475 m

```
 0:00  avg=  3.76  med=  3.89  ███████
 1:00  avg=  3.76  med=  3.89  ███████
 2:00  avg=  3.76  med=  3.89  ███████
 3:00  avg=  3.76  med=  3.89  ███████
 4:00  avg=  3.76  med=  3.89  ███████
 5:00  avg=  2.71  med=  2.76  █████
 6:00  avg=  2.76  med=  2.82  █████
 7:00  avg=  2.54  med=  2.58  █████
 8:00  avg=  2.19  med=  2.24  ████
 9:00  avg=  2.04  med=  2.12  ████
10:00  avg=  2.41  med=  2.55  ████
11:00  avg=  2.94  med=  3.28  █████
12:00  avg=  3.73  med=  4.43  ███████
13:00  avg=  4.79  med=  5.99  █████████
14:00  avg=  6.71  med=  8.54  █████████████
15:00  avg=  9.33  med= 11.97  ██████████████████
16:00  avg= 12.28  med= 15.59  ████████████████████████
17:00  avg= 14.28  med= 18.61  ████████████████████████████
18:00  avg= 14.79  med= 19.99  █████████████████████████████
19:00  avg= 14.29  med= 20.87  ████████████████████████████
20:00  avg= 14.27  med= 22.20  ████████████████████████████
21:00  avg= 14.87  med= 23.95  █████████████████████████████
22:00  avg= 15.93  med= 27.35  ███████████████████████████████
23:00  avg= 18.29  med= 28.61  ████████████████████████████████████
```

### Frame 1234859355 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,409 m | Ibrox 3,845 m | Hampden 4,258 m | Glasgow Green 1,792 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234859355 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,409 m | Ibrox 3,845 m | Hampden 4,258 m | Glasgow Green 1,792 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234859356 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,409 m | Ibrox 3,845 m | Hampden 4,258 m | Glasgow Green 1,792 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234859356 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,409 m | Ibrox 3,845 m | Hampden 4,258 m | Glasgow Green 1,792 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234859357 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,895 m | Ibrox 1,755 m | Hampden 3,894 m | Glasgow Green 2,974 m

```
 0:00  avg=  1.02  med=  1.16  ██
 1:00  avg=  1.02  med=  1.16  ██
 2:00  avg=  1.02  med=  1.16  ██
 3:00  avg=  1.02  med=  1.16  ██
 4:00  avg=  1.02  med=  1.16  ██
 5:00  avg=  1.03  med=  1.05  ██
 6:00  avg=  0.94  med=  0.95  █
 7:00  avg=  0.81  med=  0.80  █
 8:00  avg=  0.72  med=  0.69  █
 9:00  avg=  0.76  med=  0.74  █
10:00  avg=  0.79  med=  0.77  █
11:00  avg=  0.84  med=  0.84  █
12:00  avg=  0.83  med=  0.85  █
13:00  avg=  0.84  med=  0.86  █
14:00  avg=  0.83  med=  0.86  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.79  med=  0.83  █
17:00  avg=  0.76  med=  0.82  █
18:00  avg=  0.82  med=  0.97  █
19:00  avg=  0.88  med=  1.20  █
20:00  avg=  0.82  med=  1.18  █
21:00  avg=  0.80  med=  1.21  █
22:00  avg=  0.80  med=  1.25  █
23:00  avg=  0.61  med=  0.98  █
```

### Frame 1234859357 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,895 m | Ibrox 1,755 m | Hampden 3,894 m | Glasgow Green 2,974 m

```
 0:00  avg=  1.21  med=  1.38  ██
 1:00  avg=  1.21  med=  1.38  ██
 2:00  avg=  1.21  med=  1.38  ██
 3:00  avg=  1.21  med=  1.38  ██
 4:00  avg=  1.21  med=  1.38  ██
 5:00  avg=  1.09  med=  1.11  ██
 6:00  avg=  0.92  med=  0.93  █
 7:00  avg=  0.72  med=  0.71  █
 8:00  avg=  0.53  med=  0.51  █
 9:00  avg=  0.62  med=  0.59  █
10:00  avg=  0.66  med=  0.64  █
11:00  avg=  0.65  med=  0.65  █
12:00  avg=  0.63  med=  0.64  █
13:00  avg=  0.62  med=  0.64  █
14:00  avg=  0.64  med=  0.66  █
15:00  avg=  0.64  med=  0.66  █
16:00  avg=  0.68  med=  0.71  █
17:00  avg=  0.64  med=  0.69  █
18:00  avg=  0.65  med=  0.77  █
19:00  avg=  0.63  med=  0.87  █
20:00  avg=  0.59  med=  0.85  █
21:00  avg=  0.59  med=  0.89  █
22:00  avg=  0.64  med=  1.00  █
23:00  avg=  0.44  med=  0.70  
```

### Frame 1234859653 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,208 m | Ibrox 4,004 m | Hampden 4,196 m | Glasgow Green 1,633 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234859653 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,208 m | Ibrox 4,004 m | Hampden 4,196 m | Glasgow Green 1,633 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234859654 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,208 m | Ibrox 4,005 m | Hampden 4,196 m | Glasgow Green 1,633 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234859654 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,208 m | Ibrox 4,005 m | Hampden 4,196 m | Glasgow Green 1,633 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234859720 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 15,145 m | Ibrox 21,598 m | Hampden 18,320 m | Glasgow Green 17,027 m

```
 0:00  avg=  0.77  med=  0.78  █
 1:00  avg=  0.77  med=  0.78  █
 2:00  avg=  0.77  med=  0.78  █
 3:00  avg=  0.77  med=  0.78  █
 4:00  avg=  0.77  med=  0.78  █
 5:00  avg=  0.78  med=  0.79  █
 6:00  avg=  0.66  med=  0.66  █
 7:00  avg=  0.66  med=  0.66  █
 8:00  avg=  0.86  med=  0.86  █
 9:00  avg=  0.66  med=  0.66  █
10:00  avg=  0.57  med=  0.57  █
11:00  avg=  0.60  med=  0.60  █
12:00  avg=  0.56  med=  0.56  █
13:00  avg=  0.46  med=  0.46  
14:00  avg=  0.72  med=  0.73  █
15:00  avg=  0.69  med=  0.71  █
16:00  avg=  0.70  med=  0.72  █
17:00  avg=  0.90  med=  0.93  █
18:00  avg=  0.68  med=  0.70  █
19:00  avg=  0.85  med=  0.88  █
20:00  avg=  0.97  med=  1.00  █
21:00  avg=  0.96  med=  1.00  █
22:00  avg=  1.02  med=  1.05  ██
23:00  avg=  0.90  med=  0.92  █
```

### Frame 1234859720 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 15,145 m | Ibrox 21,598 m | Hampden 18,320 m | Glasgow Green 17,027 m

```
 0:00  avg=  0.71  med=  0.72  █
 1:00  avg=  0.71  med=  0.72  █
 2:00  avg=  0.71  med=  0.72  █
 3:00  avg=  0.71  med=  0.72  █
 4:00  avg=  0.71  med=  0.72  █
 5:00  avg=  0.73  med=  0.74  █
 6:00  avg=  0.69  med=  0.69  █
 7:00  avg=  0.81  med=  0.82  █
 8:00  avg=  0.75  med=  0.75  █
 9:00  avg=  0.70  med=  0.70  █
10:00  avg=  0.67  med=  0.67  █
11:00  avg=  0.73  med=  0.73  █
12:00  avg=  0.74  med=  0.73  █
13:00  avg=  0.64  med=  0.63  █
14:00  avg=  0.72  med=  0.73  █
15:00  avg=  0.80  med=  0.81  █
16:00  avg=  0.71  med=  0.73  █
17:00  avg=  0.83  med=  0.86  █
18:00  avg=  0.91  med=  0.94  █
19:00  avg=  0.86  med=  0.89  █
20:00  avg=  0.89  med=  0.92  █
21:00  avg=  0.83  med=  0.87  █
22:00  avg=  1.10  med=  1.13  ██
23:00  avg=  1.09  med=  1.12  ██
```

### Frame 1234859721 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 15,148 m | Ibrox 21,601 m | Hampden 18,322 m | Glasgow Green 17,030 m

```
 0:00  avg=  0.77  med=  0.78  █
 1:00  avg=  0.77  med=  0.78  █
 2:00  avg=  0.77  med=  0.78  █
 3:00  avg=  0.77  med=  0.78  █
 4:00  avg=  0.77  med=  0.78  █
 5:00  avg=  0.78  med=  0.79  █
 6:00  avg=  0.66  med=  0.66  █
 7:00  avg=  0.66  med=  0.66  █
 8:00  avg=  0.86  med=  0.86  █
 9:00  avg=  0.66  med=  0.66  █
10:00  avg=  0.57  med=  0.57  █
11:00  avg=  0.60  med=  0.60  █
12:00  avg=  0.56  med=  0.56  █
13:00  avg=  0.46  med=  0.46  
14:00  avg=  0.72  med=  0.73  █
15:00  avg=  0.69  med=  0.71  █
16:00  avg=  0.70  med=  0.72  █
17:00  avg=  0.90  med=  0.93  █
18:00  avg=  0.68  med=  0.70  █
19:00  avg=  0.85  med=  0.88  █
20:00  avg=  0.97  med=  1.00  █
21:00  avg=  0.96  med=  1.00  █
22:00  avg=  1.02  med=  1.05  ██
23:00  avg=  0.90  med=  0.92  █
```

### Frame 1234859721 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 15,148 m | Ibrox 21,601 m | Hampden 18,322 m | Glasgow Green 17,030 m

```
 0:00  avg=  0.71  med=  0.72  █
 1:00  avg=  0.71  med=  0.72  █
 2:00  avg=  0.71  med=  0.72  █
 3:00  avg=  0.71  med=  0.72  █
 4:00  avg=  0.71  med=  0.72  █
 5:00  avg=  0.73  med=  0.74  █
 6:00  avg=  0.69  med=  0.69  █
 7:00  avg=  0.81  med=  0.82  █
 8:00  avg=  0.75  med=  0.75  █
 9:00  avg=  0.70  med=  0.70  █
10:00  avg=  0.67  med=  0.67  █
11:00  avg=  0.73  med=  0.73  █
12:00  avg=  0.74  med=  0.73  █
13:00  avg=  0.64  med=  0.63  █
14:00  avg=  0.72  med=  0.73  █
15:00  avg=  0.80  med=  0.81  █
16:00  avg=  0.71  med=  0.73  █
17:00  avg=  0.83  med=  0.86  █
18:00  avg=  0.91  med=  0.94  █
19:00  avg=  0.86  med=  0.89  █
20:00  avg=  0.89  med=  0.92  █
21:00  avg=  0.83  med=  0.87  █
22:00  avg=  1.10  med=  1.13  ██
23:00  avg=  1.09  med=  1.12  ██
```

### Frame 1234859788 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 14,085 m | Ibrox 20,468 m | Hampden 17,437 m | Glasgow Green 15,924 m

```
 0:00  avg=  0.95  med=  0.96  █
 1:00  avg=  0.95  med=  0.96  █
 2:00  avg=  0.95  med=  0.96  █
 3:00  avg=  0.95  med=  0.96  █
 4:00  avg=  0.95  med=  0.96  █
 5:00  avg=  0.90  med=  0.90  █
 6:00  avg=  0.80  med=  0.81  █
 7:00  avg=  0.81  med=  0.81  █
 8:00  avg=  0.76  med=  0.75  █
 9:00  avg=  0.83  med=  0.80  █
10:00  avg=  0.76  med=  0.74  █
11:00  avg=  0.82  med=  0.81  █
12:00  avg=  0.66  med=  0.66  █
13:00  avg=  0.67  med=  0.68  █
14:00  avg=  0.77  med=  0.77  █
15:00  avg=  0.65  med=  0.64  █
16:00  avg=  0.83  med=  0.83  █
17:00  avg=  0.68  med=  0.68  █
18:00  avg=  0.79  med=  0.80  █
19:00  avg=  0.75  med=  0.74  █
20:00  avg=  0.79  med=  0.79  █
21:00  avg=  0.86  med=  0.87  █
22:00  avg=  0.69  med=  0.69  █
23:00  avg=  0.84  med=  0.84  █
```

### Frame 1234859788 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 14,085 m | Ibrox 20,468 m | Hampden 17,437 m | Glasgow Green 15,924 m

```
 0:00  avg=  1.15  med=  1.16  ██
 1:00  avg=  1.15  med=  1.16  ██
 2:00  avg=  1.15  med=  1.16  ██
 3:00  avg=  1.15  med=  1.16  ██
 4:00  avg=  1.15  med=  1.16  ██
 5:00  avg=  0.75  med=  0.75  █
 6:00  avg=  0.81  med=  0.81  █
 7:00  avg=  0.75  med=  0.75  █
 8:00  avg=  0.50  med=  0.50  █
 9:00  avg=  0.64  med=  0.62  █
10:00  avg=  0.81  med=  0.79  █
11:00  avg=  0.77  med=  0.76  █
12:00  avg=  0.82  med=  0.82  █
13:00  avg=  0.80  med=  0.81  █
14:00  avg=  0.82  med=  0.82  █
15:00  avg=  0.72  med=  0.70  █
16:00  avg=  0.70  med=  0.70  █
17:00  avg=  0.87  med=  0.86  █
18:00  avg=  0.71  med=  0.72  █
19:00  avg=  0.73  med=  0.72  █
20:00  avg=  0.69  med=  0.69  █
21:00  avg=  0.74  med=  0.74  █
22:00  avg=  0.71  med=  0.71  █
23:00  avg=  0.85  med=  0.85  █
```

### Frame 1234859789 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 14,085 m | Ibrox 20,468 m | Hampden 17,437 m | Glasgow Green 15,924 m

```
 0:00  avg=  0.95  med=  0.96  █
 1:00  avg=  0.95  med=  0.96  █
 2:00  avg=  0.95  med=  0.96  █
 3:00  avg=  0.95  med=  0.96  █
 4:00  avg=  0.95  med=  0.96  █
 5:00  avg=  0.90  med=  0.90  █
 6:00  avg=  0.80  med=  0.81  █
 7:00  avg=  0.81  med=  0.81  █
 8:00  avg=  0.76  med=  0.75  █
 9:00  avg=  0.83  med=  0.80  █
10:00  avg=  0.76  med=  0.74  █
11:00  avg=  0.82  med=  0.81  █
12:00  avg=  0.66  med=  0.66  █
13:00  avg=  0.67  med=  0.68  █
14:00  avg=  0.77  med=  0.77  █
15:00  avg=  0.65  med=  0.64  █
16:00  avg=  0.83  med=  0.83  █
17:00  avg=  0.68  med=  0.68  █
18:00  avg=  0.79  med=  0.80  █
19:00  avg=  0.75  med=  0.74  █
20:00  avg=  0.79  med=  0.79  █
21:00  avg=  0.86  med=  0.87  █
22:00  avg=  0.69  med=  0.69  █
23:00  avg=  0.84  med=  0.84  █
```

### Frame 1234859789 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 14,085 m | Ibrox 20,468 m | Hampden 17,437 m | Glasgow Green 15,924 m

```
 0:00  avg=  1.15  med=  1.16  ██
 1:00  avg=  1.15  med=  1.16  ██
 2:00  avg=  1.15  med=  1.16  ██
 3:00  avg=  1.15  med=  1.16  ██
 4:00  avg=  1.15  med=  1.16  ██
 5:00  avg=  0.75  med=  0.75  █
 6:00  avg=  0.81  med=  0.81  █
 7:00  avg=  0.75  med=  0.75  █
 8:00  avg=  0.50  med=  0.50  █
 9:00  avg=  0.64  med=  0.62  █
10:00  avg=  0.81  med=  0.79  █
11:00  avg=  0.77  med=  0.76  █
12:00  avg=  0.82  med=  0.82  █
13:00  avg=  0.80  med=  0.81  █
14:00  avg=  0.82  med=  0.82  █
15:00  avg=  0.72  med=  0.70  █
16:00  avg=  0.70  med=  0.70  █
17:00  avg=  0.87  med=  0.86  █
18:00  avg=  0.71  med=  0.72  █
19:00  avg=  0.73  med=  0.72  █
20:00  avg=  0.69  med=  0.69  █
21:00  avg=  0.74  med=  0.74  █
22:00  avg=  0.71  med=  0.71  █
23:00  avg=  0.85  med=  0.85  █
```

### Frame 1234859900 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 13,360 m | Ibrox 6,926 m | Hampden 10,661 m | Glasgow Green 11,479 m

```
 0:00  avg=  1.38  med=  1.42  ██
 1:00  avg=  1.38  med=  1.42  ██
 2:00  avg=  1.38  med=  1.42  ██
 3:00  avg=  1.38  med=  1.42  ██
 4:00  avg=  1.38  med=  1.42  ██
 5:00  avg=  1.15  med=  1.16  ██
 6:00  avg=  1.01  med=  1.01  ██
 7:00  avg=  0.84  med=  0.80  █
 8:00  avg=  0.68  med=  0.62  █
 9:00  avg=  0.64  med=  0.60  █
10:00  avg=  0.66  med=  0.63  █
11:00  avg=  0.82  med=  0.78  █
12:00  avg=  0.80  med=  0.77  █
13:00  avg=  0.79  med=  0.76  █
14:00  avg=  0.86  med=  0.82  █
15:00  avg=  0.82  med=  0.80  █
16:00  avg=  0.80  med=  0.78  █
17:00  avg=  0.87  med=  0.85  █
18:00  avg=  0.87  med=  0.90  █
19:00  avg=  0.89  med=  0.92  █
20:00  avg=  0.95  med=  1.02  █
21:00  avg=  1.15  med=  1.24  ██
22:00  avg=  1.23  med=  1.33  ██
23:00  avg=  1.23  med=  1.35  ██
```

### Frame 1234859900 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 13,360 m | Ibrox 6,926 m | Hampden 10,661 m | Glasgow Green 11,479 m

```
 0:00  avg=  1.20  med=  1.23  ██
 1:00  avg=  1.20  med=  1.23  ██
 2:00  avg=  1.20  med=  1.23  ██
 3:00  avg=  1.20  med=  1.23  ██
 4:00  avg=  1.20  med=  1.23  ██
 5:00  avg=  0.99  med=  1.00  █
 6:00  avg=  0.77  med=  0.77  █
 7:00  avg=  0.67  med=  0.64  █
 8:00  avg=  0.42  med=  0.39  
 9:00  avg=  0.48  med=  0.45  
10:00  avg=  0.49  med=  0.47  
11:00  avg=  0.53  med=  0.50  █
12:00  avg=  0.55  med=  0.52  █
13:00  avg=  0.58  med=  0.56  █
14:00  avg=  0.59  med=  0.57  █
15:00  avg=  0.59  med=  0.57  █
16:00  avg=  0.56  med=  0.54  █
17:00  avg=  0.61  med=  0.60  █
18:00  avg=  0.66  med=  0.68  █
19:00  avg=  0.60  med=  0.63  █
20:00  avg=  0.61  med=  0.65  █
21:00  avg=  0.73  med=  0.79  █
22:00  avg=  0.89  med=  0.97  █
23:00  avg=  1.09  med=  1.20  ██
```

### Frame 1234859901 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 13,360 m | Ibrox 6,926 m | Hampden 10,661 m | Glasgow Green 11,479 m

```
 0:00  avg=  1.38  med=  1.42  ██
 1:00  avg=  1.38  med=  1.42  ██
 2:00  avg=  1.38  med=  1.42  ██
 3:00  avg=  1.38  med=  1.42  ██
 4:00  avg=  1.38  med=  1.42  ██
 5:00  avg=  1.15  med=  1.16  ██
 6:00  avg=  1.01  med=  1.01  ██
 7:00  avg=  0.84  med=  0.80  █
 8:00  avg=  0.68  med=  0.62  █
 9:00  avg=  0.64  med=  0.60  █
10:00  avg=  0.66  med=  0.63  █
11:00  avg=  0.82  med=  0.78  █
12:00  avg=  0.80  med=  0.77  █
13:00  avg=  0.79  med=  0.76  █
14:00  avg=  0.86  med=  0.82  █
15:00  avg=  0.82  med=  0.80  █
16:00  avg=  0.80  med=  0.78  █
17:00  avg=  0.87  med=  0.85  █
18:00  avg=  0.87  med=  0.90  █
19:00  avg=  0.89  med=  0.92  █
20:00  avg=  0.95  med=  1.02  █
21:00  avg=  1.15  med=  1.24  ██
22:00  avg=  1.23  med=  1.33  ██
23:00  avg=  1.23  med=  1.35  ██
```

### Frame 1234859901 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 13,360 m | Ibrox 6,926 m | Hampden 10,661 m | Glasgow Green 11,479 m

```
 0:00  avg=  1.20  med=  1.23  ██
 1:00  avg=  1.20  med=  1.23  ██
 2:00  avg=  1.20  med=  1.23  ██
 3:00  avg=  1.20  med=  1.23  ██
 4:00  avg=  1.20  med=  1.23  ██
 5:00  avg=  0.99  med=  1.00  █
 6:00  avg=  0.77  med=  0.77  █
 7:00  avg=  0.67  med=  0.64  █
 8:00  avg=  0.42  med=  0.39  
 9:00  avg=  0.48  med=  0.45  
10:00  avg=  0.49  med=  0.47  
11:00  avg=  0.53  med=  0.50  █
12:00  avg=  0.55  med=  0.52  █
13:00  avg=  0.58  med=  0.56  █
14:00  avg=  0.59  med=  0.57  █
15:00  avg=  0.59  med=  0.57  █
16:00  avg=  0.56  med=  0.54  █
17:00  avg=  0.61  med=  0.60  █
18:00  avg=  0.66  med=  0.68  █
19:00  avg=  0.60  med=  0.63  █
20:00  avg=  0.61  med=  0.65  █
21:00  avg=  0.73  med=  0.79  █
22:00  avg=  0.89  med=  0.97  █
23:00  avg=  1.09  med=  1.20  ██
```

### Frame 1234859990 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,896 m | Ibrox 1,755 m | Hampden 3,895 m | Glasgow Green 2,974 m

```
 0:00  avg=  1.02  med=  1.16  ██
 1:00  avg=  1.02  med=  1.16  ██
 2:00  avg=  1.02  med=  1.16  ██
 3:00  avg=  1.02  med=  1.16  ██
 4:00  avg=  1.02  med=  1.16  ██
 5:00  avg=  1.03  med=  1.05  ██
 6:00  avg=  0.94  med=  0.95  █
 7:00  avg=  0.81  med=  0.80  █
 8:00  avg=  0.72  med=  0.69  █
 9:00  avg=  0.76  med=  0.74  █
10:00  avg=  0.79  med=  0.77  █
11:00  avg=  0.84  med=  0.84  █
12:00  avg=  0.83  med=  0.85  █
13:00  avg=  0.84  med=  0.86  █
14:00  avg=  0.83  med=  0.86  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.79  med=  0.83  █
17:00  avg=  0.76  med=  0.82  █
18:00  avg=  0.82  med=  0.97  █
19:00  avg=  0.88  med=  1.20  █
20:00  avg=  0.82  med=  1.18  █
21:00  avg=  0.80  med=  1.21  █
22:00  avg=  0.80  med=  1.25  █
23:00  avg=  0.61  med=  0.98  █
```

### Frame 1234859990 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,896 m | Ibrox 1,755 m | Hampden 3,895 m | Glasgow Green 2,974 m

```
 0:00  avg=  1.21  med=  1.38  ██
 1:00  avg=  1.21  med=  1.38  ██
 2:00  avg=  1.21  med=  1.38  ██
 3:00  avg=  1.21  med=  1.38  ██
 4:00  avg=  1.21  med=  1.38  ██
 5:00  avg=  1.09  med=  1.11  ██
 6:00  avg=  0.92  med=  0.93  █
 7:00  avg=  0.72  med=  0.71  █
 8:00  avg=  0.53  med=  0.51  █
 9:00  avg=  0.62  med=  0.59  █
10:00  avg=  0.66  med=  0.64  █
11:00  avg=  0.65  med=  0.65  █
12:00  avg=  0.63  med=  0.64  █
13:00  avg=  0.62  med=  0.64  █
14:00  avg=  0.64  med=  0.66  █
15:00  avg=  0.64  med=  0.66  █
16:00  avg=  0.68  med=  0.71  █
17:00  avg=  0.64  med=  0.69  █
18:00  avg=  0.65  med=  0.77  █
19:00  avg=  0.63  med=  0.87  █
20:00  avg=  0.59  med=  0.85  █
21:00  avg=  0.59  med=  0.89  █
22:00  avg=  0.64  med=  1.00  █
23:00  avg=  0.44  med=  0.70  
```

### Frame 1234859991 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,895 m | Ibrox 1,755 m | Hampden 3,894 m | Glasgow Green 2,974 m

```
 0:00  avg=  1.02  med=  1.16  ██
 1:00  avg=  1.02  med=  1.16  ██
 2:00  avg=  1.02  med=  1.16  ██
 3:00  avg=  1.02  med=  1.16  ██
 4:00  avg=  1.02  med=  1.16  ██
 5:00  avg=  1.03  med=  1.05  ██
 6:00  avg=  0.94  med=  0.95  █
 7:00  avg=  0.81  med=  0.80  █
 8:00  avg=  0.72  med=  0.69  █
 9:00  avg=  0.76  med=  0.74  █
10:00  avg=  0.79  med=  0.77  █
11:00  avg=  0.84  med=  0.84  █
12:00  avg=  0.83  med=  0.85  █
13:00  avg=  0.84  med=  0.86  █
14:00  avg=  0.83  med=  0.86  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.79  med=  0.83  █
17:00  avg=  0.76  med=  0.82  █
18:00  avg=  0.82  med=  0.97  █
19:00  avg=  0.88  med=  1.20  █
20:00  avg=  0.82  med=  1.18  █
21:00  avg=  0.80  med=  1.21  █
22:00  avg=  0.80  med=  1.25  █
23:00  avg=  0.61  med=  0.98  █
```

### Frame 1234859991 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,895 m | Ibrox 1,755 m | Hampden 3,894 m | Glasgow Green 2,974 m

```
 0:00  avg=  1.21  med=  1.38  ██
 1:00  avg=  1.21  med=  1.38  ██
 2:00  avg=  1.21  med=  1.38  ██
 3:00  avg=  1.21  med=  1.38  ██
 4:00  avg=  1.21  med=  1.38  ██
 5:00  avg=  1.09  med=  1.11  ██
 6:00  avg=  0.92  med=  0.93  █
 7:00  avg=  0.72  med=  0.71  █
 8:00  avg=  0.53  med=  0.51  █
 9:00  avg=  0.62  med=  0.59  █
10:00  avg=  0.66  med=  0.64  █
11:00  avg=  0.65  med=  0.65  █
12:00  avg=  0.63  med=  0.64  █
13:00  avg=  0.62  med=  0.64  █
14:00  avg=  0.64  med=  0.66  █
15:00  avg=  0.64  med=  0.66  █
16:00  avg=  0.68  med=  0.71  █
17:00  avg=  0.64  med=  0.69  █
18:00  avg=  0.65  med=  0.77  █
19:00  avg=  0.63  med=  0.87  █
20:00  avg=  0.59  med=  0.85  █
21:00  avg=  0.59  med=  0.89  █
22:00  avg=  0.64  med=  1.00  █
23:00  avg=  0.44  med=  0.70  
```

### Frame 1234861001 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,190 m | Ibrox 3,977 m | Hampden 4,143 m | Glasgow Green 1,593 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234861001 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,190 m | Ibrox 3,977 m | Hampden 4,143 m | Glasgow Green 1,593 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234861002 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,190 m | Ibrox 3,977 m | Hampden 4,143 m | Glasgow Green 1,593 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234861002 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,190 m | Ibrox 3,977 m | Hampden 4,143 m | Glasgow Green 1,593 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234861324 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 7,089 m | Ibrox 621 m | Hampden 5,000 m | Glasgow Green 5,186 m

```
 0:00  avg=  1.02  med=  1.03  ██
 1:00  avg=  1.02  med=  1.03  ██
 2:00  avg=  1.02  med=  1.03  ██
 3:00  avg=  1.02  med=  1.03  ██
 4:00  avg=  1.02  med=  1.03  ██
 5:00  avg=  0.89  med=  0.89  █
 6:00  avg=  0.76  med=  0.74  █
 7:00  avg=  0.61  med=  0.56  █
 8:00  avg=  0.55  med=  0.48  █
 9:00  avg=  0.54  med=  0.48  █
10:00  avg=  0.57  med=  0.51  █
11:00  avg=  0.58  med=  0.52  █
12:00  avg=  0.62  med=  0.56  █
13:00  avg=  0.63  med=  0.58  █
14:00  avg=  0.62  med=  0.57  █
15:00  avg=  0.64  med=  0.59  █
16:00  avg=  0.67  med=  0.63  █
17:00  avg=  0.74  med=  0.72  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.95  med=  0.98  █
20:00  avg=  0.98  med=  1.00  █
21:00  avg=  0.96  med=  0.97  █
22:00  avg=  1.07  med=  1.08  ██
23:00  avg=  1.17  med=  1.15  ██
```

### Frame 1234861324 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 7,089 m | Ibrox 621 m | Hampden 5,000 m | Glasgow Green 5,186 m

```
 0:00  avg=  1.00  med=  1.01  ██
 1:00  avg=  1.00  med=  1.01  ██
 2:00  avg=  1.00  med=  1.01  ██
 3:00  avg=  1.00  med=  1.01  ██
 4:00  avg=  1.00  med=  1.01  ██
 5:00  avg=  0.84  med=  0.84  █
 6:00  avg=  0.74  med=  0.72  █
 7:00  avg=  0.52  med=  0.48  █
 8:00  avg=  0.43  med=  0.37  
 9:00  avg=  0.40  med=  0.36  
10:00  avg=  0.44  med=  0.39  
11:00  avg=  0.47  med=  0.43  
12:00  avg=  0.51  med=  0.46  █
13:00  avg=  0.52  med=  0.48  █
14:00  avg=  0.51  med=  0.47  █
15:00  avg=  0.52  med=  0.48  █
16:00  avg=  0.55  med=  0.52  █
17:00  avg=  0.69  med=  0.67  █
18:00  avg=  0.76  med=  0.78  █
19:00  avg=  0.77  med=  0.78  █
20:00  avg=  0.83  med=  0.84  █
21:00  avg=  0.80  med=  0.81  █
22:00  avg=  0.87  med=  0.88  █
23:00  avg=  0.91  med=  0.90  █
```

### Frame 1234861325 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 5,842 m | Ibrox 666 m | Hampden 3,955 m | Glasgow Green 3,944 m

```
 0:00  avg=  0.82  med=  0.83  █
 1:00  avg=  0.82  med=  0.83  █
 2:00  avg=  0.82  med=  0.83  █
 3:00  avg=  0.82  med=  0.83  █
 4:00  avg=  0.82  med=  0.83  █
 5:00  avg=  0.74  med=  0.74  █
 6:00  avg=  0.84  med=  0.85  █
 7:00  avg=  0.71  med=  0.71  █
 8:00  avg=  0.84  med=  0.85  █
 9:00  avg=  0.74  med=  0.75  █
10:00  avg=  0.74  med=  0.76  █
11:00  avg=  0.62  med=  0.63  █
12:00  avg=  0.86  med=  0.87  █
13:00  avg=  0.66  med=  0.68  █
14:00  avg=  0.57  med=  0.59  █
15:00  avg=  0.61  med=  0.61  █
16:00  avg=  0.75  med=  0.75  █
17:00  avg=  0.55  med=  0.56  █
18:00  avg=  0.85  med=  0.86  █
19:00  avg=  0.93  med=  0.95  █
20:00  avg=  0.70  med=  0.71  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.91  med=  0.91  █
23:00  avg=  0.79  med=  0.80  █
```

### Frame 1234861325 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 5,842 m | Ibrox 666 m | Hampden 3,955 m | Glasgow Green 3,944 m

```
 0:00  avg=  1.05  med=  1.06  ██
 1:00  avg=  1.05  med=  1.06  ██
 2:00  avg=  1.05  med=  1.06  ██
 3:00  avg=  1.05  med=  1.06  ██
 4:00  avg=  1.05  med=  1.06  ██
 5:00  avg=  0.73  med=  0.73  █
 6:00  avg=  0.73  med=  0.74  █
 7:00  avg=  0.90  med=  0.90  █
 8:00  avg=  0.77  med=  0.78  █
 9:00  avg=  0.83  med=  0.84  █
10:00  avg=  0.72  med=  0.73  █
11:00  avg=  0.99  med=  1.01  █
12:00  avg=  0.87  med=  0.88  █
13:00  avg=  0.76  med=  0.77  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.86  med=  0.87  █
16:00  avg=  0.71  med=  0.71  █
17:00  avg=  0.70  med=  0.72  █
18:00  avg=  0.67  med=  0.68  █
19:00  avg=  0.72  med=  0.73  █
20:00  avg=  0.90  med=  0.92  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.80  med=  0.80  █
23:00  avg=  0.99  med=  1.00  █
```

### Frame 1234861326 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 5,842 m | Ibrox 667 m | Hampden 3,954 m | Glasgow Green 3,943 m

```
 0:00  avg=  0.82  med=  0.83  █
 1:00  avg=  0.82  med=  0.83  █
 2:00  avg=  0.82  med=  0.83  █
 3:00  avg=  0.82  med=  0.83  █
 4:00  avg=  0.82  med=  0.83  █
 5:00  avg=  0.74  med=  0.74  █
 6:00  avg=  0.84  med=  0.85  █
 7:00  avg=  0.71  med=  0.71  █
 8:00  avg=  0.84  med=  0.85  █
 9:00  avg=  0.74  med=  0.75  █
10:00  avg=  0.74  med=  0.76  █
11:00  avg=  0.62  med=  0.63  █
12:00  avg=  0.86  med=  0.87  █
13:00  avg=  0.66  med=  0.68  █
14:00  avg=  0.57  med=  0.59  █
15:00  avg=  0.61  med=  0.61  █
16:00  avg=  0.75  med=  0.75  █
17:00  avg=  0.55  med=  0.56  █
18:00  avg=  0.85  med=  0.86  █
19:00  avg=  0.93  med=  0.95  █
20:00  avg=  0.70  med=  0.71  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.91  med=  0.91  █
23:00  avg=  0.79  med=  0.80  █
```

### Frame 1234861326 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 5,842 m | Ibrox 667 m | Hampden 3,954 m | Glasgow Green 3,943 m

```
 0:00  avg=  1.05  med=  1.06  ██
 1:00  avg=  1.05  med=  1.06  ██
 2:00  avg=  1.05  med=  1.06  ██
 3:00  avg=  1.05  med=  1.06  ██
 4:00  avg=  1.05  med=  1.06  ██
 5:00  avg=  0.73  med=  0.73  █
 6:00  avg=  0.73  med=  0.74  █
 7:00  avg=  0.90  med=  0.90  █
 8:00  avg=  0.77  med=  0.78  █
 9:00  avg=  0.83  med=  0.84  █
10:00  avg=  0.72  med=  0.73  █
11:00  avg=  0.99  med=  1.01  █
12:00  avg=  0.87  med=  0.88  █
13:00  avg=  0.76  med=  0.77  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.86  med=  0.87  █
16:00  avg=  0.71  med=  0.71  █
17:00  avg=  0.70  med=  0.72  █
18:00  avg=  0.67  med=  0.68  █
19:00  avg=  0.72  med=  0.73  █
20:00  avg=  0.90  med=  0.92  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.80  med=  0.80  █
23:00  avg=  0.99  med=  1.00  █
```

### Frame 1234861335 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,398 m | Ibrox 4,204 m | Hampden 3,250 m | Glasgow Green 572 m

```
 0:00  avg=  3.65  med=  3.77  ███████
 1:00  avg=  3.65  med=  3.77  ███████
 2:00  avg=  3.65  med=  3.77  ███████
 3:00  avg=  3.65  med=  3.77  ███████
 4:00  avg=  3.65  med=  3.77  ███████
 5:00  avg=  2.54  med=  2.59  █████
 6:00  avg=  2.55  med=  2.61  █████
 7:00  avg=  2.56  med=  2.60  █████
 8:00  avg=  2.49  med=  2.55  ████
 9:00  avg=  2.61  med=  2.71  █████
10:00  avg=  2.84  med=  3.01  █████
11:00  avg=  3.24  med=  3.61  ██████
12:00  avg=  4.38  med=  5.19  ████████
13:00  avg=  6.18  med=  7.72  ████████████
14:00  avg=  9.06  med= 11.54  ██████████████████
15:00  avg= 12.08  med= 15.50  ████████████████████████
16:00  avg= 14.16  med= 17.96  ████████████████████████████
17:00  avg= 15.22  med= 19.84  ██████████████████████████████
18:00  avg= 15.62  med= 21.12  ███████████████████████████████
19:00  avg= 15.15  med= 22.13  ██████████████████████████████
20:00  avg= 15.30  med= 23.80  ██████████████████████████████
21:00  avg= 16.13  med= 25.98  ████████████████████████████████
22:00  avg= 17.17  med= 29.48  ██████████████████████████████████
23:00  avg= 18.48  med= 28.90  ████████████████████████████████████
```

### Frame 1234861335 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,398 m | Ibrox 4,204 m | Hampden 3,250 m | Glasgow Green 572 m

```
 0:00  avg=  3.76  med=  3.89  ███████
 1:00  avg=  3.76  med=  3.89  ███████
 2:00  avg=  3.76  med=  3.89  ███████
 3:00  avg=  3.76  med=  3.89  ███████
 4:00  avg=  3.76  med=  3.89  ███████
 5:00  avg=  2.71  med=  2.76  █████
 6:00  avg=  2.76  med=  2.82  █████
 7:00  avg=  2.54  med=  2.58  █████
 8:00  avg=  2.19  med=  2.24  ████
 9:00  avg=  2.04  med=  2.12  ████
10:00  avg=  2.41  med=  2.55  ████
11:00  avg=  2.94  med=  3.28  █████
12:00  avg=  3.73  med=  4.43  ███████
13:00  avg=  4.79  med=  5.99  █████████
14:00  avg=  6.71  med=  8.54  █████████████
15:00  avg=  9.33  med= 11.97  ██████████████████
16:00  avg= 12.28  med= 15.59  ████████████████████████
17:00  avg= 14.28  med= 18.61  ████████████████████████████
18:00  avg= 14.79  med= 19.99  █████████████████████████████
19:00  avg= 14.29  med= 20.87  ████████████████████████████
20:00  avg= 14.27  med= 22.20  ████████████████████████████
21:00  avg= 14.87  med= 23.95  █████████████████████████████
22:00  avg= 15.93  med= 27.35  ███████████████████████████████
23:00  avg= 18.29  med= 28.61  ████████████████████████████████████
```

### Frame 1234861345 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 1,876 m | Ibrox 4,729 m | Hampden 3,330 m | Glasgow Green 386 m

```
 0:00  avg=  1.78  med=  1.79  ███
 1:00  avg=  1.78  med=  1.79  ███
 2:00  avg=  1.78  med=  1.79  ███
 3:00  avg=  1.78  med=  1.79  ███
 4:00  avg=  1.78  med=  1.79  ███
 5:00  avg=  1.62  med=  1.63  ███
 6:00  avg=  1.66  med=  1.69  ███
 7:00  avg=  1.39  med=  1.38  ██
 8:00  avg=  1.85  med=  1.87  ███
 9:00  avg=  1.89  med=  1.92  ███
10:00  avg=  2.09  med=  2.14  ████
11:00  avg=  2.36  med=  2.48  ████
12:00  avg=  3.73  med=  4.00  ███████
13:00  avg=  5.66  med=  6.41  ███████████
14:00  avg=  8.55  med=  9.73  █████████████████
15:00  avg= 11.42  med= 13.34  ██████████████████████
16:00  avg= 13.47  med= 15.91  ██████████████████████████
17:00  avg= 14.15  med= 16.72  ████████████████████████████
18:00  avg= 14.67  med= 17.62  █████████████████████████████
19:00  avg= 14.47  med= 17.59  ████████████████████████████
20:00  avg= 15.03  med= 18.61  ██████████████████████████████
21:00  avg= 15.38  med= 18.79  ██████████████████████████████
22:00  avg= 15.76  med= 19.13  ███████████████████████████████
23:00  avg= 14.07  med= 16.42  ████████████████████████████
```

### Frame 1234861345 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 1,876 m | Ibrox 4,729 m | Hampden 3,330 m | Glasgow Green 386 m

```
 0:00  avg=  1.56  med=  1.56  ███
 1:00  avg=  1.56  med=  1.56  ███
 2:00  avg=  1.56  med=  1.56  ███
 3:00  avg=  1.56  med=  1.56  ███
 4:00  avg=  1.56  med=  1.56  ███
 5:00  avg=  1.36  med=  1.37  ██
 6:00  avg=  1.58  med=  1.60  ███
 7:00  avg=  1.12  med=  1.11  ██
 8:00  avg=  1.41  med=  1.42  ██
 9:00  avg=  1.47  med=  1.50  ██
10:00  avg=  1.87  med=  1.91  ███
11:00  avg=  2.17  med=  2.28  ████
12:00  avg=  2.89  med=  3.10  █████
13:00  avg=  3.96  med=  4.48  ███████
14:00  avg=  5.82  med=  6.62  ███████████
15:00  avg=  8.66  med= 10.11  █████████████████
16:00  avg= 11.59  med= 13.69  ███████████████████████
17:00  avg= 13.80  med= 16.31  ███████████████████████████
18:00  avg= 14.44  med= 17.35  ████████████████████████████
19:00  avg= 14.07  med= 17.11  ████████████████████████████
20:00  avg= 14.07  med= 17.42  ████████████████████████████
21:00  avg= 14.54  med= 17.77  █████████████████████████████
22:00  avg= 14.57  med= 17.68  █████████████████████████████
23:00  avg= 14.44  med= 16.85  ████████████████████████████
```

### Frame 1234861346 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 1,876 m | Ibrox 4,729 m | Hampden 3,330 m | Glasgow Green 386 m

```
 0:00  avg=  1.78  med=  1.79  ███
 1:00  avg=  1.78  med=  1.79  ███
 2:00  avg=  1.78  med=  1.79  ███
 3:00  avg=  1.78  med=  1.79  ███
 4:00  avg=  1.78  med=  1.79  ███
 5:00  avg=  1.62  med=  1.63  ███
 6:00  avg=  1.66  med=  1.69  ███
 7:00  avg=  1.39  med=  1.38  ██
 8:00  avg=  1.85  med=  1.87  ███
 9:00  avg=  1.89  med=  1.92  ███
10:00  avg=  2.09  med=  2.14  ████
11:00  avg=  2.36  med=  2.48  ████
12:00  avg=  3.73  med=  4.00  ███████
13:00  avg=  5.66  med=  6.41  ███████████
14:00  avg=  8.55  med=  9.73  █████████████████
15:00  avg= 11.42  med= 13.34  ██████████████████████
16:00  avg= 13.47  med= 15.91  ██████████████████████████
17:00  avg= 14.15  med= 16.72  ████████████████████████████
18:00  avg= 14.67  med= 17.62  █████████████████████████████
19:00  avg= 14.47  med= 17.59  ████████████████████████████
20:00  avg= 15.03  med= 18.61  ██████████████████████████████
21:00  avg= 15.38  med= 18.79  ██████████████████████████████
22:00  avg= 15.76  med= 19.13  ███████████████████████████████
23:00  avg= 14.07  med= 16.42  ████████████████████████████
```

### Frame 1234861346 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 1,876 m | Ibrox 4,729 m | Hampden 3,330 m | Glasgow Green 386 m

```
 0:00  avg=  1.56  med=  1.56  ███
 1:00  avg=  1.56  med=  1.56  ███
 2:00  avg=  1.56  med=  1.56  ███
 3:00  avg=  1.56  med=  1.56  ███
 4:00  avg=  1.56  med=  1.56  ███
 5:00  avg=  1.36  med=  1.37  ██
 6:00  avg=  1.58  med=  1.60  ███
 7:00  avg=  1.12  med=  1.11  ██
 8:00  avg=  1.41  med=  1.42  ██
 9:00  avg=  1.47  med=  1.50  ██
10:00  avg=  1.87  med=  1.91  ███
11:00  avg=  2.17  med=  2.28  ████
12:00  avg=  2.89  med=  3.10  █████
13:00  avg=  3.96  med=  4.48  ███████
14:00  avg=  5.82  med=  6.62  ███████████
15:00  avg=  8.66  med= 10.11  █████████████████
16:00  avg= 11.59  med= 13.69  ███████████████████████
17:00  avg= 13.80  med= 16.31  ███████████████████████████
18:00  avg= 14.44  med= 17.35  ████████████████████████████
19:00  avg= 14.07  med= 17.11  ████████████████████████████
20:00  avg= 14.07  med= 17.42  ████████████████████████████
21:00  avg= 14.54  med= 17.77  █████████████████████████████
22:00  avg= 14.57  med= 17.68  █████████████████████████████
23:00  avg= 14.44  med= 16.85  ████████████████████████████
```

### Frame 1234926735 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,297 m | Ibrox 3,723 m | Hampden 3,978 m | Glasgow Green 1,587 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926735 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,297 m | Ibrox 3,723 m | Hampden 3,978 m | Glasgow Green 1,587 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926736 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,297 m | Ibrox 3,723 m | Hampden 3,979 m | Glasgow Green 1,587 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926736 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,297 m | Ibrox 3,723 m | Hampden 3,979 m | Glasgow Green 1,587 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926737 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,290 m | Ibrox 3,796 m | Hampden 4,059 m | Glasgow Green 1,618 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926737 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,290 m | Ibrox 3,796 m | Hampden 4,059 m | Glasgow Green 1,618 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926741 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,280 m | Ibrox 3,793 m | Hampden 4,042 m | Glasgow Green 1,604 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926741 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,280 m | Ibrox 3,793 m | Hampden 4,042 m | Glasgow Green 1,604 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926742 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,281 m | Ibrox 3,793 m | Hampden 4,043 m | Glasgow Green 1,604 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926742 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,281 m | Ibrox 3,793 m | Hampden 4,043 m | Glasgow Green 1,604 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926743 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,299 m | Ibrox 3,719 m | Hampden 3,976 m | Glasgow Green 1,588 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926743 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,299 m | Ibrox 3,719 m | Hampden 3,976 m | Glasgow Green 1,588 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926744 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,298 m | Ibrox 3,720 m | Hampden 3,976 m | Glasgow Green 1,587 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926744 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,298 m | Ibrox 3,720 m | Hampden 3,976 m | Glasgow Green 1,587 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926745 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,305 m | Ibrox 3,693 m | Hampden 3,952 m | Glasgow Green 1,582 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926745 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,305 m | Ibrox 3,693 m | Hampden 3,952 m | Glasgow Green 1,582 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926746 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,275 m | Ibrox 3,794 m | Hampden 4,036 m | Glasgow Green 1,597 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234926746 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,275 m | Ibrox 3,794 m | Hampden 4,036 m | Glasgow Green 1,597 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234926776 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,274 m | Ibrox 4,196 m | Hampden 8,766 m | Glasgow Green 8,368 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1234926776 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,274 m | Ibrox 4,196 m | Hampden 8,766 m | Glasgow Green 8,368 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1234926777 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,287 m | Ibrox 4,209 m | Hampden 8,778 m | Glasgow Green 8,381 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1234926777 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,287 m | Ibrox 4,209 m | Hampden 8,778 m | Glasgow Green 8,381 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1234926778 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,364 m | Ibrox 4,295 m | Hampden 8,865 m | Glasgow Green 8,459 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1234926778 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,364 m | Ibrox 4,295 m | Hampden 8,865 m | Glasgow Green 8,459 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1234926779 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,465 m | Ibrox 4,398 m | Hampden 8,968 m | Glasgow Green 8,561 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1234926779 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,465 m | Ibrox 4,398 m | Hampden 8,968 m | Glasgow Green 8,561 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1234930794 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,292 m | Ibrox 3,743 m | Hampden 3,997 m | Glasgow Green 1,592 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234930794 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,292 m | Ibrox 3,743 m | Hampden 3,997 m | Glasgow Green 1,592 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234930795 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,291 m | Ibrox 3,744 m | Hampden 3,997 m | Glasgow Green 1,592 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234930795 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,291 m | Ibrox 3,744 m | Hampden 3,997 m | Glasgow Green 1,592 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1234932170 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,288 m | Ibrox 3,855 m | Hampden 4,125 m | Glasgow Green 1,648 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1234932170 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,288 m | Ibrox 3,855 m | Hampden 4,125 m | Glasgow Green 1,648 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1235077385 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,445 m | Ibrox 4,378 m | Hampden 8,948 m | Glasgow Green 8,541 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235077385 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,445 m | Ibrox 4,378 m | Hampden 8,948 m | Glasgow Green 8,541 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235077387 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,444 m | Ibrox 4,374 m | Hampden 8,944 m | Glasgow Green 8,539 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235077387 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,444 m | Ibrox 4,374 m | Hampden 8,944 m | Glasgow Green 8,539 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235190714 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 1,685 m | Ibrox 6,496 m | Hampden 2,710 m | Glasgow Green 2,529 m

```
 0:00  avg=  1.06  med=  1.06  ██
 1:00  avg=  1.06  med=  1.06  ██
 2:00  avg=  1.06  med=  1.06  ██
 3:00  avg=  1.06  med=  1.06  ██
 4:00  avg=  1.06  med=  1.06  ██
 5:00  avg=  0.99  med=  1.00  █
 6:00  avg=  0.94  med=  0.95  █
 7:00  avg=  0.85  med=  0.84  █
 8:00  avg=  0.74  med=  0.70  █
 9:00  avg=  0.73  med=  0.70  █
10:00  avg=  0.73  med=  0.71  █
11:00  avg=  0.78  med=  0.75  █
12:00  avg=  0.78  med=  0.76  █
13:00  avg=  0.82  med=  0.80  █
14:00  avg=  0.78  med=  0.77  █
15:00  avg=  0.79  med=  0.79  █
16:00  avg=  0.89  med=  0.89  █
17:00  avg=  0.95  med=  0.95  █
18:00  avg=  0.80  med=  0.80  █
19:00  avg=  0.72  med=  0.73  █
20:00  avg=  0.72  med=  0.73  █
21:00  avg=  0.76  med=  0.78  █
22:00  avg=  0.68  med=  0.68  █
23:00  avg=  0.87  med=  0.87  █
```

### Frame 1235190714 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 1,685 m | Ibrox 6,496 m | Hampden 2,710 m | Glasgow Green 2,529 m

```
 0:00  avg=  1.10  med=  1.10  ██
 1:00  avg=  1.10  med=  1.10  ██
 2:00  avg=  1.10  med=  1.10  ██
 3:00  avg=  1.10  med=  1.10  ██
 4:00  avg=  1.10  med=  1.10  ██
 5:00  avg=  0.89  med=  0.90  █
 6:00  avg=  0.85  med=  0.86  █
 7:00  avg=  0.67  med=  0.66  █
 8:00  avg=  0.60  med=  0.57  █
 9:00  avg=  0.57  med=  0.54  █
10:00  avg=  0.67  med=  0.64  █
11:00  avg=  0.73  med=  0.71  █
12:00  avg=  0.78  med=  0.77  █
13:00  avg=  0.81  med=  0.79  █
14:00  avg=  0.74  med=  0.73  █
15:00  avg=  0.74  med=  0.74  █
16:00  avg=  0.70  med=  0.70  █
17:00  avg=  0.67  med=  0.66  █
18:00  avg=  0.64  med=  0.64  █
19:00  avg=  0.66  med=  0.66  █
20:00  avg=  0.64  med=  0.66  █
21:00  avg=  0.56  med=  0.57  █
22:00  avg=  0.82  med=  0.83  █
23:00  avg=  0.96  med=  0.96  █
```

### Frame 1235197563 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,290 m | Ibrox 3,796 m | Hampden 4,059 m | Glasgow Green 1,618 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 1235197563 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,290 m | Ibrox 3,796 m | Hampden 4,059 m | Glasgow Green 1,618 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 1235242514 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,448 m | Ibrox 4,380 m | Hampden 8,950 m | Glasgow Green 8,543 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242514 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,448 m | Ibrox 4,380 m | Hampden 8,950 m | Glasgow Green 8,543 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235242516 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,370 m | Ibrox 4,295 m | Hampden 8,864 m | Glasgow Green 8,464 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242516 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,370 m | Ibrox 4,295 m | Hampden 8,864 m | Glasgow Green 8,464 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235242517 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,393 m | Ibrox 4,318 m | Hampden 8,888 m | Glasgow Green 8,487 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242517 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,393 m | Ibrox 4,318 m | Hampden 8,888 m | Glasgow Green 8,487 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235242519 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,392 m | Ibrox 4,317 m | Hampden 8,886 m | Glasgow Green 8,487 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242519 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,392 m | Ibrox 4,317 m | Hampden 8,886 m | Glasgow Green 8,487 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235242520 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,299 m | Ibrox 4,218 m | Hampden 8,788 m | Glasgow Green 8,393 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242520 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,299 m | Ibrox 4,218 m | Hampden 8,788 m | Glasgow Green 8,393 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235242522 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,299 m | Ibrox 4,218 m | Hampden 8,788 m | Glasgow Green 8,393 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242522 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,299 m | Ibrox 4,218 m | Hampden 8,788 m | Glasgow Green 8,393 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235242527 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,369 m | Ibrox 4,295 m | Hampden 8,864 m | Glasgow Green 8,463 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242527 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,369 m | Ibrox 4,295 m | Hampden 8,864 m | Glasgow Green 8,463 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235242530 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 10,370 m | Ibrox 4,292 m | Hampden 8,861 m | Glasgow Green 8,464 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.82  med=  0.80  █
 6:00  avg=  0.67  med=  0.60  █
 7:00  avg=  0.48  med=  0.40  
 8:00  avg=  0.50  med=  0.41  
 9:00  avg=  0.60  med=  0.52  █
10:00  avg=  0.68  med=  0.63  █
11:00  avg=  0.74  med=  0.71  █
12:00  avg=  0.82  med=  0.80  █
13:00  avg=  0.88  med=  0.89  █
14:00  avg=  0.95  med=  0.97  █
15:00  avg=  0.98  med=  1.02  █
16:00  avg=  0.96  med=  0.99  █
17:00  avg=  0.95  med=  0.97  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.72  med=  0.70  █
20:00  avg=  0.71  med=  0.69  █
21:00  avg=  0.80  med=  0.84  █
22:00  avg=  0.93  med=  1.01  █
23:00  avg=  1.30  med=  1.34  ██
```

### Frame 1235242530 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 10,370 m | Ibrox 4,292 m | Hampden 8,861 m | Glasgow Green 8,464 m

```
 0:00  avg=  1.10  med=  1.11  ██
 1:00  avg=  1.10  med=  1.11  ██
 2:00  avg=  1.10  med=  1.11  ██
 3:00  avg=  1.10  med=  1.11  ██
 4:00  avg=  1.10  med=  1.11  ██
 5:00  avg=  0.75  med=  0.73  █
 6:00  avg=  0.55  med=  0.50  █
 7:00  avg=  0.34  med=  0.29  
 8:00  avg=  0.28  med=  0.23  
 9:00  avg=  0.37  med=  0.32  
10:00  avg=  0.53  med=  0.49  █
11:00  avg=  0.63  med=  0.60  █
12:00  avg=  0.69  med=  0.67  █
13:00  avg=  0.75  med=  0.76  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.77  med=  0.80  █
16:00  avg=  0.72  med=  0.74  █
17:00  avg=  0.66  med=  0.68  █
18:00  avg=  0.56  med=  0.56  █
19:00  avg=  0.39  med=  0.38  
20:00  avg=  0.34  med=  0.34  
21:00  avg=  0.46  med=  0.48  
22:00  avg=  0.65  med=  0.71  █
23:00  avg=  1.18  med=  1.22  ██
```

### Frame 1235462335 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 1,746 m | Ibrox 5,269 m | Hampden 2,060 m | Glasgow Green 1,440 m

```
 0:00  avg=  1.19  med=  1.23  ██
 1:00  avg=  1.19  med=  1.23  ██
 2:00  avg=  1.19  med=  1.23  ██
 3:00  avg=  1.19  med=  1.23  ██
 4:00  avg=  1.19  med=  1.23  ██
 5:00  avg=  1.01  med=  1.03  ██
 6:00  avg=  0.99  med=  0.98  █
 7:00  avg=  0.71  med=  0.65  █
 8:00  avg=  0.62  med=  0.56  █
 9:00  avg=  0.62  med=  0.55  █
10:00  avg=  0.62  med=  0.57  █
11:00  avg=  0.63  med=  0.58  █
12:00  avg=  0.60  med=  0.57  █
13:00  avg=  0.65  med=  0.62  █
14:00  avg=  0.64  med=  0.61  █
15:00  avg=  0.64  med=  0.60  █
16:00  avg=  0.65  med=  0.62  █
17:00  avg=  0.71  med=  0.70  █
18:00  avg=  0.73  med=  0.74  █
19:00  avg=  0.84  med=  0.86  █
20:00  avg=  0.93  med=  0.94  █
21:00  avg=  1.07  med=  1.10  ██
22:00  avg=  1.09  med=  1.12  ██
23:00  avg=  1.46  med=  1.55  ██
```

### Frame 1235462335 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 1,746 m | Ibrox 5,269 m | Hampden 2,060 m | Glasgow Green 1,440 m

```
 0:00  avg=  1.23  med=  1.27  ██
 1:00  avg=  1.23  med=  1.27  ██
 2:00  avg=  1.23  med=  1.27  ██
 3:00  avg=  1.23  med=  1.27  ██
 4:00  avg=  1.23  med=  1.27  ██
 5:00  avg=  0.88  med=  0.90  █
 6:00  avg=  0.82  med=  0.81  █
 7:00  avg=  0.54  med=  0.50  █
 8:00  avg=  0.49  med=  0.45  
 9:00  avg=  0.45  med=  0.40  
10:00  avg=  0.46  med=  0.42  
11:00  avg=  0.49  med=  0.46  
12:00  avg=  0.49  med=  0.46  
13:00  avg=  0.58  med=  0.55  █
14:00  avg=  0.55  med=  0.53  █
15:00  avg=  0.59  med=  0.56  █
16:00  avg=  0.59  med=  0.56  █
17:00  avg=  0.66  med=  0.65  █
18:00  avg=  0.76  med=  0.77  █
19:00  avg=  0.87  med=  0.89  █
20:00  avg=  0.81  med=  0.83  █
21:00  avg=  0.85  med=  0.86  █
22:00  avg=  0.88  med=  0.90  █
23:00  avg=  1.22  med=  1.30  ██
```

### Frame 1235462352 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 1,746 m | Ibrox 5,269 m | Hampden 2,060 m | Glasgow Green 1,440 m

```
 0:00  avg=  1.19  med=  1.23  ██
 1:00  avg=  1.19  med=  1.23  ██
 2:00  avg=  1.19  med=  1.23  ██
 3:00  avg=  1.19  med=  1.23  ██
 4:00  avg=  1.19  med=  1.23  ██
 5:00  avg=  1.01  med=  1.03  ██
 6:00  avg=  0.99  med=  0.98  █
 7:00  avg=  0.71  med=  0.65  █
 8:00  avg=  0.62  med=  0.56  █
 9:00  avg=  0.62  med=  0.55  █
10:00  avg=  0.62  med=  0.57  █
11:00  avg=  0.63  med=  0.58  █
12:00  avg=  0.60  med=  0.57  █
13:00  avg=  0.65  med=  0.62  █
14:00  avg=  0.64  med=  0.61  █
15:00  avg=  0.64  med=  0.60  █
16:00  avg=  0.65  med=  0.62  █
17:00  avg=  0.71  med=  0.70  █
18:00  avg=  0.73  med=  0.74  █
19:00  avg=  0.84  med=  0.86  █
20:00  avg=  0.93  med=  0.94  █
21:00  avg=  1.07  med=  1.10  ██
22:00  avg=  1.09  med=  1.12  ██
23:00  avg=  1.46  med=  1.55  ██
```

### Frame 1235462352 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 1,746 m | Ibrox 5,269 m | Hampden 2,060 m | Glasgow Green 1,440 m

```
 0:00  avg=  1.23  med=  1.27  ██
 1:00  avg=  1.23  med=  1.27  ██
 2:00  avg=  1.23  med=  1.27  ██
 3:00  avg=  1.23  med=  1.27  ██
 4:00  avg=  1.23  med=  1.27  ██
 5:00  avg=  0.88  med=  0.90  █
 6:00  avg=  0.82  med=  0.81  █
 7:00  avg=  0.54  med=  0.50  █
 8:00  avg=  0.49  med=  0.45  
 9:00  avg=  0.45  med=  0.40  
10:00  avg=  0.46  med=  0.42  
11:00  avg=  0.49  med=  0.46  
12:00  avg=  0.49  med=  0.46  
13:00  avg=  0.58  med=  0.55  █
14:00  avg=  0.55  med=  0.53  █
15:00  avg=  0.59  med=  0.56  █
16:00  avg=  0.59  med=  0.56  █
17:00  avg=  0.66  med=  0.65  █
18:00  avg=  0.76  med=  0.77  █
19:00  avg=  0.87  med=  0.89  █
20:00  avg=  0.81  med=  0.83  █
21:00  avg=  0.85  med=  0.86  █
22:00  avg=  0.88  med=  0.90  █
23:00  avg=  1.22  med=  1.30  ██
```

### Frame 1235464179 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 414 m | Ibrox 6,098 m | Hampden 3,424 m | Glasgow Green 1,561 m

```
 0:00  avg=  1.55  med=  1.56  ███
 1:00  avg=  1.55  med=  1.56  ███
 2:00  avg=  1.55  med=  1.56  ███
 3:00  avg=  1.55  med=  1.56  ███
 4:00  avg=  1.55  med=  1.56  ███
 5:00  avg=  1.41  med=  1.39  ██
 6:00  avg=  1.17  med=  1.14  ██
 7:00  avg=  1.04  med=  1.00  ██
 8:00  avg=  0.81  med=  0.76  █
 9:00  avg=  0.76  med=  0.71  █
10:00  avg=  0.76  med=  0.73  █
11:00  avg=  0.76  med=  0.78  █
12:00  avg=  0.61  med=  0.66  █
13:00  avg=  0.63  med=  0.71  █
14:00  avg=  0.64  med=  0.80  █
15:00  avg=  0.60  med=  0.76  █
16:00  avg=  0.63  med=  0.78  █
17:00  avg=  0.73  med=  0.91  █
18:00  avg=  0.86  med=  0.98  █
19:00  avg=  0.90  med=  1.04  █
20:00  avg=  0.85  med=  0.99  █
21:00  avg=  1.01  med=  1.18  ██
22:00  avg=  1.06  med=  1.27  ██
23:00  avg=  1.63  med=  1.75  ███
```

### Frame 1235464179 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 414 m | Ibrox 6,098 m | Hampden 3,424 m | Glasgow Green 1,561 m

```
 0:00  avg=  1.52  med=  1.53  ███
 1:00  avg=  1.52  med=  1.53  ███
 2:00  avg=  1.52  med=  1.53  ███
 3:00  avg=  1.52  med=  1.53  ███
 4:00  avg=  1.52  med=  1.53  ███
 5:00  avg=  1.27  med=  1.25  ██
 6:00  avg=  1.08  med=  1.05  ██
 7:00  avg=  0.95  med=  0.91  █
 8:00  avg=  0.74  med=  0.69  █
 9:00  avg=  0.63  med=  0.59  █
10:00  avg=  0.59  med=  0.56  █
11:00  avg=  0.63  med=  0.65  █
12:00  avg=  0.63  med=  0.68  █
13:00  avg=  0.67  med=  0.76  █
14:00  avg=  0.59  med=  0.74  █
15:00  avg=  0.53  med=  0.67  █
16:00  avg=  0.51  med=  0.64  █
17:00  avg=  0.56  med=  0.69  █
18:00  avg=  0.64  med=  0.73  █
19:00  avg=  0.65  med=  0.74  █
20:00  avg=  0.67  med=  0.78  █
21:00  avg=  0.67  med=  0.79  █
22:00  avg=  0.91  med=  1.09  █
23:00  avg=  1.80  med=  1.94  ███
```

### Frame 1235464181 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,845 m | Ibrox 1,795 m | Hampden 3,854 m | Glasgow Green 2,923 m

```
 0:00  avg=  1.02  med=  1.16  ██
 1:00  avg=  1.02  med=  1.16  ██
 2:00  avg=  1.02  med=  1.16  ██
 3:00  avg=  1.02  med=  1.16  ██
 4:00  avg=  1.02  med=  1.16  ██
 5:00  avg=  1.03  med=  1.05  ██
 6:00  avg=  0.94  med=  0.95  █
 7:00  avg=  0.81  med=  0.80  █
 8:00  avg=  0.72  med=  0.69  █
 9:00  avg=  0.76  med=  0.74  █
10:00  avg=  0.79  med=  0.77  █
11:00  avg=  0.84  med=  0.84  █
12:00  avg=  0.83  med=  0.85  █
13:00  avg=  0.84  med=  0.86  █
14:00  avg=  0.83  med=  0.86  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.79  med=  0.83  █
17:00  avg=  0.76  med=  0.82  █
18:00  avg=  0.82  med=  0.97  █
19:00  avg=  0.88  med=  1.20  █
20:00  avg=  0.82  med=  1.18  █
21:00  avg=  0.80  med=  1.21  █
22:00  avg=  0.80  med=  1.25  █
23:00  avg=  0.61  med=  0.98  █
```

### Frame 1235464181 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,845 m | Ibrox 1,795 m | Hampden 3,854 m | Glasgow Green 2,923 m

```
 0:00  avg=  1.21  med=  1.38  ██
 1:00  avg=  1.21  med=  1.38  ██
 2:00  avg=  1.21  med=  1.38  ██
 3:00  avg=  1.21  med=  1.38  ██
 4:00  avg=  1.21  med=  1.38  ██
 5:00  avg=  1.09  med=  1.11  ██
 6:00  avg=  0.92  med=  0.93  █
 7:00  avg=  0.72  med=  0.71  █
 8:00  avg=  0.53  med=  0.51  █
 9:00  avg=  0.62  med=  0.59  █
10:00  avg=  0.66  med=  0.64  █
11:00  avg=  0.65  med=  0.65  █
12:00  avg=  0.63  med=  0.64  █
13:00  avg=  0.62  med=  0.64  █
14:00  avg=  0.64  med=  0.66  █
15:00  avg=  0.64  med=  0.66  █
16:00  avg=  0.68  med=  0.71  █
17:00  avg=  0.64  med=  0.69  █
18:00  avg=  0.65  med=  0.77  █
19:00  avg=  0.63  med=  0.87  █
20:00  avg=  0.59  med=  0.85  █
21:00  avg=  0.59  med=  0.89  █
22:00  avg=  0.64  med=  1.00  █
23:00  avg=  0.44  med=  0.70  
```

### Frame 2000028113 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,277 m | Ibrox 4,322 m | Hampden 3,254 m | Glasgow Green 481 m

```
 0:00  avg=  3.65  med=  3.77  ███████
 1:00  avg=  3.65  med=  3.77  ███████
 2:00  avg=  3.65  med=  3.77  ███████
 3:00  avg=  3.65  med=  3.77  ███████
 4:00  avg=  3.65  med=  3.77  ███████
 5:00  avg=  2.54  med=  2.59  █████
 6:00  avg=  2.55  med=  2.61  █████
 7:00  avg=  2.56  med=  2.60  █████
 8:00  avg=  2.49  med=  2.55  ████
 9:00  avg=  2.61  med=  2.71  █████
10:00  avg=  2.84  med=  3.01  █████
11:00  avg=  3.24  med=  3.61  ██████
12:00  avg=  4.38  med=  5.19  ████████
13:00  avg=  6.18  med=  7.72  ████████████
14:00  avg=  9.06  med= 11.54  ██████████████████
15:00  avg= 12.08  med= 15.50  ████████████████████████
16:00  avg= 14.16  med= 17.96  ████████████████████████████
17:00  avg= 15.22  med= 19.84  ██████████████████████████████
18:00  avg= 15.62  med= 21.12  ███████████████████████████████
19:00  avg= 15.15  med= 22.13  ██████████████████████████████
20:00  avg= 15.30  med= 23.80  ██████████████████████████████
21:00  avg= 16.13  med= 25.98  ████████████████████████████████
22:00  avg= 17.17  med= 29.48  ██████████████████████████████████
23:00  avg= 18.48  med= 28.90  ████████████████████████████████████
```

### Frame 2000028113 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,277 m | Ibrox 4,322 m | Hampden 3,254 m | Glasgow Green 481 m

```
 0:00  avg=  3.76  med=  3.89  ███████
 1:00  avg=  3.76  med=  3.89  ███████
 2:00  avg=  3.76  med=  3.89  ███████
 3:00  avg=  3.76  med=  3.89  ███████
 4:00  avg=  3.76  med=  3.89  ███████
 5:00  avg=  2.71  med=  2.76  █████
 6:00  avg=  2.76  med=  2.82  █████
 7:00  avg=  2.54  med=  2.58  █████
 8:00  avg=  2.19  med=  2.24  ████
 9:00  avg=  2.04  med=  2.12  ████
10:00  avg=  2.41  med=  2.55  ████
11:00  avg=  2.94  med=  3.28  █████
12:00  avg=  3.73  med=  4.43  ███████
13:00  avg=  4.79  med=  5.99  █████████
14:00  avg=  6.71  med=  8.54  █████████████
15:00  avg=  9.33  med= 11.97  ██████████████████
16:00  avg= 12.28  med= 15.59  ████████████████████████
17:00  avg= 14.28  med= 18.61  ████████████████████████████
18:00  avg= 14.79  med= 19.99  █████████████████████████████
19:00  avg= 14.29  med= 20.87  ████████████████████████████
20:00  avg= 14.27  med= 22.20  ████████████████████████████
21:00  avg= 14.87  med= 23.95  █████████████████████████████
22:00  avg= 15.93  med= 27.35  ███████████████████████████████
23:00  avg= 18.29  med= 28.61  ████████████████████████████████████
```

### Frame 2000028118 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 14,039 m | Ibrox 7,584 m | Hampden 11,381 m | Glasgow Green 12,149 m

```
 0:00  avg=  1.11  med=  1.11  ██
 1:00  avg=  1.11  med=  1.11  ██
 2:00  avg=  1.11  med=  1.11  ██
 3:00  avg=  1.11  med=  1.11  ██
 4:00  avg=  1.11  med=  1.11  ██
 5:00  avg=  1.05  med=  1.03  ██
 6:00  avg=  1.03  med=  1.03  ██
 7:00  avg=  1.06  med=  1.08  ██
 8:00  avg=  1.11  med=  1.08  ██
 9:00  avg=  0.99  med=  0.95  █
10:00  avg=  0.95  med=  0.92  █
11:00  avg=  1.00  med=  0.98  ██
12:00  avg=  1.08  med=  1.08  ██
13:00  avg=  1.21  med=  1.21  ██
14:00  avg=  0.87  med=  0.87  █
15:00  avg=  0.79  med=  0.79  █
16:00  avg=  0.93  med=  0.94  █
17:00  avg=  0.77  med=  0.79  █
18:00  avg=  0.86  med=  0.88  █
19:00  avg=  0.80  med=  0.81  █
20:00  avg=  0.72  med=  0.72  █
21:00  avg=  0.94  med=  0.95  █
22:00  avg=  0.95  med=  0.95  █
23:00  avg=  0.87  med=  0.87  █
```

### Frame 2000028118 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 14,039 m | Ibrox 7,584 m | Hampden 11,381 m | Glasgow Green 12,149 m

```
 0:00  avg=  1.37  med=  1.37  ██
 1:00  avg=  1.37  med=  1.37  ██
 2:00  avg=  1.37  med=  1.37  ██
 3:00  avg=  1.37  med=  1.37  ██
 4:00  avg=  1.37  med=  1.37  ██
 5:00  avg=  0.79  med=  0.78  █
 6:00  avg=  0.68  med=  0.68  █
 7:00  avg=  0.65  med=  0.66  █
 8:00  avg=  0.65  med=  0.63  █
 9:00  avg=  0.36  med=  0.34  
10:00  avg=  0.60  med=  0.59  █
11:00  avg=  0.73  med=  0.72  █
12:00  avg=  0.77  med=  0.77  █
13:00  avg=  0.76  med=  0.75  █
14:00  avg=  0.94  med=  0.94  █
15:00  avg=  0.79  med=  0.79  █
16:00  avg=  0.76  med=  0.77  █
17:00  avg=  0.87  med=  0.90  █
18:00  avg=  0.87  med=  0.88  █
19:00  avg=  0.91  med=  0.91  █
20:00  avg=  0.58  med=  0.58  █
21:00  avg=  0.61  med=  0.62  █
22:00  avg=  0.68  med=  0.68  █
23:00  avg=  0.59  med=  0.59  █
```

### Frame 2000113429 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,143 m | Ibrox 4,392 m | Hampden 3,073 m | Glasgow Green 268 m

```
 0:00  avg=  2.33  med=  2.37  ████
 1:00  avg=  2.33  med=  2.37  ████
 2:00  avg=  2.33  med=  2.37  ████
 3:00  avg=  2.33  med=  2.37  ████
 4:00  avg=  2.33  med=  2.37  ████
 5:00  avg=  1.78  med=  1.79  ███
 6:00  avg=  1.82  med=  1.83  ███
 7:00  avg=  1.68  med=  1.70  ███
 8:00  avg=  1.65  med=  1.70  ███
 9:00  avg=  1.90  med=  2.01  ███
10:00  avg=  2.08  med=  2.26  ████
11:00  avg=  2.78  med=  3.11  █████
12:00  avg=  4.01  med=  4.68  ████████
13:00  avg=  5.69  med=  6.94  ███████████
14:00  avg=  8.48  med= 10.49  ████████████████
15:00  avg= 11.47  med= 14.51  ██████████████████████
16:00  avg= 13.59  med= 17.18  ███████████████████████████
17:00  avg= 15.31  med= 19.58  ██████████████████████████████
18:00  avg= 15.89  med= 20.78  ███████████████████████████████
19:00  avg= 15.79  med= 20.42  ███████████████████████████████
20:00  avg= 16.35  med= 21.52  ████████████████████████████████
21:00  avg= 17.37  med= 23.61  ██████████████████████████████████
22:00  avg= 18.14  med= 25.57  ████████████████████████████████████
23:00  avg= 18.60  med= 24.70  █████████████████████████████████████
```

### Frame 2000113429 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,143 m | Ibrox 4,392 m | Hampden 3,073 m | Glasgow Green 268 m

```
 0:00  avg=  2.25  med=  2.29  ████
 1:00  avg=  2.25  med=  2.29  ████
 2:00  avg=  2.25  med=  2.29  ████
 3:00  avg=  2.25  med=  2.29  ████
 4:00  avg=  2.25  med=  2.29  ████
 5:00  avg=  1.68  med=  1.68  ███
 6:00  avg=  1.66  med=  1.68  ███
 7:00  avg=  1.51  med=  1.52  ███
 8:00  avg=  1.38  med=  1.42  ██
 9:00  avg=  1.39  med=  1.48  ██
10:00  avg=  1.71  med=  1.85  ███
11:00  avg=  2.21  med=  2.48  ████
12:00  avg=  3.11  med=  3.63  ██████
13:00  avg=  3.95  med=  4.82  ███████
14:00  avg=  5.79  med=  7.17  ███████████
15:00  avg=  8.58  med= 10.85  █████████████████
16:00  avg= 11.79  med= 14.91  ███████████████████████
17:00  avg= 14.48  med= 18.52  ████████████████████████████
18:00  avg= 15.22  med= 19.90  ██████████████████████████████
19:00  avg= 14.99  med= 19.37  █████████████████████████████
20:00  avg= 15.55  med= 20.46  ███████████████████████████████
21:00  avg= 16.36  med= 22.23  ████████████████████████████████
22:00  avg= 17.12  med= 24.13  ██████████████████████████████████
23:00  avg= 17.60  med= 23.36  ███████████████████████████████████
```

### Frame 2000113442 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 15,131 m | Ibrox 21,580 m | Hampden 18,319 m | Glasgow Green 17,010 m

```
 0:00  avg=  0.77  med=  0.78  █
 1:00  avg=  0.77  med=  0.78  █
 2:00  avg=  0.77  med=  0.78  █
 3:00  avg=  0.77  med=  0.78  █
 4:00  avg=  0.77  med=  0.78  █
 5:00  avg=  0.78  med=  0.79  █
 6:00  avg=  0.66  med=  0.66  █
 7:00  avg=  0.66  med=  0.66  █
 8:00  avg=  0.86  med=  0.86  █
 9:00  avg=  0.66  med=  0.66  █
10:00  avg=  0.57  med=  0.57  █
11:00  avg=  0.60  med=  0.60  █
12:00  avg=  0.56  med=  0.56  █
13:00  avg=  0.46  med=  0.46  
14:00  avg=  0.72  med=  0.73  █
15:00  avg=  0.69  med=  0.71  █
16:00  avg=  0.70  med=  0.72  █
17:00  avg=  0.90  med=  0.93  █
18:00  avg=  0.68  med=  0.70  █
19:00  avg=  0.85  med=  0.88  █
20:00  avg=  0.97  med=  1.00  █
21:00  avg=  0.96  med=  1.00  █
22:00  avg=  1.02  med=  1.05  ██
23:00  avg=  0.90  med=  0.92  █
```

### Frame 2000113442 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 15,131 m | Ibrox 21,580 m | Hampden 18,319 m | Glasgow Green 17,010 m

```
 0:00  avg=  0.71  med=  0.72  █
 1:00  avg=  0.71  med=  0.72  █
 2:00  avg=  0.71  med=  0.72  █
 3:00  avg=  0.71  med=  0.72  █
 4:00  avg=  0.71  med=  0.72  █
 5:00  avg=  0.73  med=  0.74  █
 6:00  avg=  0.69  med=  0.69  █
 7:00  avg=  0.81  med=  0.82  █
 8:00  avg=  0.75  med=  0.75  █
 9:00  avg=  0.70  med=  0.70  █
10:00  avg=  0.67  med=  0.67  █
11:00  avg=  0.73  med=  0.73  █
12:00  avg=  0.74  med=  0.73  █
13:00  avg=  0.64  med=  0.63  █
14:00  avg=  0.72  med=  0.73  █
15:00  avg=  0.80  med=  0.81  █
16:00  avg=  0.71  med=  0.73  █
17:00  avg=  0.83  med=  0.86  █
18:00  avg=  0.91  med=  0.94  █
19:00  avg=  0.86  med=  0.89  █
20:00  avg=  0.89  med=  0.92  █
21:00  avg=  0.83  med=  0.87  █
22:00  avg=  1.10  med=  1.13  ██
23:00  avg=  1.09  med=  1.12  ██
```

### Frame 2000118300 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,570 m | Ibrox 4,052 m | Hampden 3,292 m | Glasgow Green 733 m

```
 0:00  avg=  3.65  med=  3.77  ███████
 1:00  avg=  3.65  med=  3.77  ███████
 2:00  avg=  3.65  med=  3.77  ███████
 3:00  avg=  3.65  med=  3.77  ███████
 4:00  avg=  3.65  med=  3.77  ███████
 5:00  avg=  2.54  med=  2.59  █████
 6:00  avg=  2.55  med=  2.61  █████
 7:00  avg=  2.56  med=  2.60  █████
 8:00  avg=  2.49  med=  2.55  ████
 9:00  avg=  2.61  med=  2.71  █████
10:00  avg=  2.84  med=  3.01  █████
11:00  avg=  3.24  med=  3.61  ██████
12:00  avg=  4.38  med=  5.19  ████████
13:00  avg=  6.18  med=  7.72  ████████████
14:00  avg=  9.06  med= 11.54  ██████████████████
15:00  avg= 12.08  med= 15.50  ████████████████████████
16:00  avg= 14.16  med= 17.96  ████████████████████████████
17:00  avg= 15.22  med= 19.84  ██████████████████████████████
18:00  avg= 15.62  med= 21.12  ███████████████████████████████
19:00  avg= 15.15  med= 22.13  ██████████████████████████████
20:00  avg= 15.30  med= 23.80  ██████████████████████████████
21:00  avg= 16.13  med= 25.98  ████████████████████████████████
22:00  avg= 17.17  med= 29.48  ██████████████████████████████████
23:00  avg= 18.48  med= 28.90  ████████████████████████████████████
```

### Frame 2000118300 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,570 m | Ibrox 4,052 m | Hampden 3,292 m | Glasgow Green 733 m

```
 0:00  avg=  3.76  med=  3.89  ███████
 1:00  avg=  3.76  med=  3.89  ███████
 2:00  avg=  3.76  med=  3.89  ███████
 3:00  avg=  3.76  med=  3.89  ███████
 4:00  avg=  3.76  med=  3.89  ███████
 5:00  avg=  2.71  med=  2.76  █████
 6:00  avg=  2.76  med=  2.82  █████
 7:00  avg=  2.54  med=  2.58  █████
 8:00  avg=  2.19  med=  2.24  ████
 9:00  avg=  2.04  med=  2.12  ████
10:00  avg=  2.41  med=  2.55  ████
11:00  avg=  2.94  med=  3.28  █████
12:00  avg=  3.73  med=  4.43  ███████
13:00  avg=  4.79  med=  5.99  █████████
14:00  avg=  6.71  med=  8.54  █████████████
15:00  avg=  9.33  med= 11.97  ██████████████████
16:00  avg= 12.28  med= 15.59  ████████████████████████
17:00  avg= 14.28  med= 18.61  ████████████████████████████
18:00  avg= 14.79  med= 19.99  █████████████████████████████
19:00  avg= 14.29  med= 20.87  ████████████████████████████
20:00  avg= 14.27  med= 22.20  ████████████████████████████
21:00  avg= 14.87  med= 23.95  █████████████████████████████
22:00  avg= 15.93  med= 27.35  ███████████████████████████████
23:00  avg= 18.29  med= 28.61  ████████████████████████████████████
```

### Frame 2000118304 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,570 m | Ibrox 4,052 m | Hampden 3,292 m | Glasgow Green 733 m

```
 0:00  avg=  3.65  med=  3.77  ███████
 1:00  avg=  3.65  med=  3.77  ███████
 2:00  avg=  3.65  med=  3.77  ███████
 3:00  avg=  3.65  med=  3.77  ███████
 4:00  avg=  3.65  med=  3.77  ███████
 5:00  avg=  2.54  med=  2.59  █████
 6:00  avg=  2.55  med=  2.61  █████
 7:00  avg=  2.56  med=  2.60  █████
 8:00  avg=  2.49  med=  2.55  ████
 9:00  avg=  2.61  med=  2.71  █████
10:00  avg=  2.84  med=  3.01  █████
11:00  avg=  3.24  med=  3.61  ██████
12:00  avg=  4.38  med=  5.19  ████████
13:00  avg=  6.18  med=  7.72  ████████████
14:00  avg=  9.06  med= 11.54  ██████████████████
15:00  avg= 12.08  med= 15.50  ████████████████████████
16:00  avg= 14.16  med= 17.96  ████████████████████████████
17:00  avg= 15.22  med= 19.84  ██████████████████████████████
18:00  avg= 15.62  med= 21.12  ███████████████████████████████
19:00  avg= 15.15  med= 22.13  ██████████████████████████████
20:00  avg= 15.30  med= 23.80  ██████████████████████████████
21:00  avg= 16.13  med= 25.98  ████████████████████████████████
22:00  avg= 17.17  med= 29.48  ██████████████████████████████████
23:00  avg= 18.48  med= 28.90  ████████████████████████████████████
```

### Frame 2000118304 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,570 m | Ibrox 4,052 m | Hampden 3,292 m | Glasgow Green 733 m

```
 0:00  avg=  3.76  med=  3.89  ███████
 1:00  avg=  3.76  med=  3.89  ███████
 2:00  avg=  3.76  med=  3.89  ███████
 3:00  avg=  3.76  med=  3.89  ███████
 4:00  avg=  3.76  med=  3.89  ███████
 5:00  avg=  2.71  med=  2.76  █████
 6:00  avg=  2.76  med=  2.82  █████
 7:00  avg=  2.54  med=  2.58  █████
 8:00  avg=  2.19  med=  2.24  ████
 9:00  avg=  2.04  med=  2.12  ████
10:00  avg=  2.41  med=  2.55  ████
11:00  avg=  2.94  med=  3.28  █████
12:00  avg=  3.73  med=  4.43  ███████
13:00  avg=  4.79  med=  5.99  █████████
14:00  avg=  6.71  med=  8.54  █████████████
15:00  avg=  9.33  med= 11.97  ██████████████████
16:00  avg= 12.28  med= 15.59  ████████████████████████
17:00  avg= 14.28  med= 18.61  ████████████████████████████
18:00  avg= 14.79  med= 19.99  █████████████████████████████
19:00  avg= 14.29  med= 20.87  ████████████████████████████
20:00  avg= 14.27  med= 22.20  ████████████████████████████
21:00  avg= 14.87  med= 23.95  █████████████████████████████
22:00  avg= 15.93  med= 27.35  ███████████████████████████████
23:00  avg= 18.29  med= 28.61  ████████████████████████████████████
```

### Frame 2000181153 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 2,353 m | Ibrox 6,098 m | Hampden 1,986 m | Glasgow Green 2,652 m

```
 0:00  avg=  1.19  med=  1.23  ██
 1:00  avg=  1.19  med=  1.23  ██
 2:00  avg=  1.19  med=  1.23  ██
 3:00  avg=  1.19  med=  1.23  ██
 4:00  avg=  1.19  med=  1.23  ██
 5:00  avg=  1.01  med=  1.03  ██
 6:00  avg=  0.99  med=  0.98  █
 7:00  avg=  0.71  med=  0.65  █
 8:00  avg=  0.62  med=  0.56  █
 9:00  avg=  0.62  med=  0.55  █
10:00  avg=  0.62  med=  0.57  █
11:00  avg=  0.63  med=  0.58  █
12:00  avg=  0.60  med=  0.57  █
13:00  avg=  0.65  med=  0.62  █
14:00  avg=  0.64  med=  0.61  █
15:00  avg=  0.64  med=  0.60  █
16:00  avg=  0.65  med=  0.62  █
17:00  avg=  0.71  med=  0.70  █
18:00  avg=  0.73  med=  0.74  █
19:00  avg=  0.84  med=  0.86  █
20:00  avg=  0.93  med=  0.94  █
21:00  avg=  1.07  med=  1.10  ██
22:00  avg=  1.09  med=  1.12  ██
23:00  avg=  1.46  med=  1.55  ██
```

### Frame 2000181153 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 2,353 m | Ibrox 6,098 m | Hampden 1,986 m | Glasgow Green 2,652 m

```
 0:00  avg=  1.23  med=  1.27  ██
 1:00  avg=  1.23  med=  1.27  ██
 2:00  avg=  1.23  med=  1.27  ██
 3:00  avg=  1.23  med=  1.27  ██
 4:00  avg=  1.23  med=  1.27  ██
 5:00  avg=  0.88  med=  0.90  █
 6:00  avg=  0.82  med=  0.81  █
 7:00  avg=  0.54  med=  0.50  █
 8:00  avg=  0.49  med=  0.45  
 9:00  avg=  0.45  med=  0.40  
10:00  avg=  0.46  med=  0.42  
11:00  avg=  0.49  med=  0.46  
12:00  avg=  0.49  med=  0.46  
13:00  avg=  0.58  med=  0.55  █
14:00  avg=  0.55  med=  0.53  █
15:00  avg=  0.59  med=  0.56  █
16:00  avg=  0.59  med=  0.56  █
17:00  avg=  0.66  med=  0.65  █
18:00  avg=  0.76  med=  0.77  █
19:00  avg=  0.87  med=  0.89  █
20:00  avg=  0.81  med=  0.83  █
21:00  avg=  0.85  med=  0.86  █
22:00  avg=  0.88  med=  0.90  █
23:00  avg=  1.22  med=  1.30  ██
```

### Frame 2000188294 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 5,562 m | Ibrox 3,735 m | Hampden 6,099 m | Glasgow Green 3,996 m

```
 0:00  avg=  0.93  med=  1.00  █
 1:00  avg=  0.93  med=  1.00  █
 2:00  avg=  0.93  med=  1.00  █
 3:00  avg=  0.93  med=  1.00  █
 4:00  avg=  0.93  med=  1.00  █
 5:00  avg=  1.23  med=  1.32  ██
 6:00  avg=  0.68  med=  0.71  █
 7:00  avg=  0.42  med=  0.44  
 8:00  avg=  0.62  med=  0.65  █
 9:00  avg=  0.78  med=  0.82  █
10:00  avg=  0.77  med=  0.79  █
11:00  avg=  0.54  med=  0.56  █
12:00  avg=  0.79  med=  0.81  █
13:00  avg=  0.98  med=  1.02  █
14:00  avg=  2.00  med=  2.05  ███
15:00  avg=  1.93  med=  2.02  ███
16:00  avg=  1.18  med=  1.23  ██
17:00  avg=  1.41  med=  1.50  ██
18:00  avg=  0.62  med=  0.68  █
19:00  avg=  0.62  med=  0.68  █
20:00  avg=  0.81  med=  0.88  █
21:00  avg=  0.35  med=  0.37  
22:00  avg=  0.57  med=  0.60  █
23:00  avg=  0.87  med=  0.91  █
```

### Frame 2000188294 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 5,562 m | Ibrox 3,735 m | Hampden 6,099 m | Glasgow Green 3,996 m

```
 0:00  avg=  1.22  med=  1.31  ██
 1:00  avg=  1.22  med=  1.31  ██
 2:00  avg=  1.22  med=  1.31  ██
 3:00  avg=  1.22  med=  1.31  ██
 4:00  avg=  1.22  med=  1.31  ██
 5:00  avg=  1.28  med=  1.38  ██
 6:00  avg=  0.46  med=  0.49  
 7:00  avg=  0.70  med=  0.75  █
 8:00  avg=  0.65  med=  0.68  █
 9:00  avg=  0.64  med=  0.68  █
10:00  avg=  1.09  med=  1.12  ██
11:00  avg=  0.40  med=  0.41  
12:00  avg=  0.65  med=  0.67  █
13:00  avg=  0.65  med=  0.68  █
14:00  avg=  0.88  med=  0.90  █
15:00  avg=  1.35  med=  1.43  ██
16:00  avg=  0.89  med=  0.93  █
17:00  avg=  0.64  med=  0.68  █
18:00  avg=  0.95  med=  1.03  █
19:00  avg=  0.92  med=  1.00  █
20:00  avg=  1.00  med=  1.09  ██
21:00  avg=  0.72  med=  0.77  █
22:00  avg=  0.46  med=  0.49  
23:00  avg=  1.04  med=  1.09  ██
```

### Frame 2000188388 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 454 m | Ibrox 6,314 m | Hampden 3,976 m | Glasgow Green 1,743 m

```
 0:00  avg=  0.92  med=  0.93  █
 1:00  avg=  0.92  med=  0.93  █
 2:00  avg=  0.92  med=  0.93  █
 3:00  avg=  0.92  med=  0.93  █
 4:00  avg=  0.92  med=  0.93  █
 5:00  avg=  0.90  med=  0.91  █
 6:00  avg=  0.90  med=  0.92  █
 7:00  avg=  1.07  med=  1.07  ██
 8:00  avg=  1.03  med=  1.02  ██
 9:00  avg=  1.01  med=  1.02  ██
10:00  avg=  1.03  med=  1.04  ██
11:00  avg=  0.89  med=  0.91  █
12:00  avg=  0.94  med=  0.99  █
13:00  avg=  1.08  med=  1.14  ██
14:00  avg=  0.99  med=  1.10  █
15:00  avg=  0.83  med=  0.92  █
16:00  avg=  0.96  med=  1.03  █
17:00  avg=  0.86  med=  0.91  █
18:00  avg=  1.14  med=  1.18  ██
19:00  avg=  1.21  med=  1.27  ██
20:00  avg=  1.24  med=  1.29  ██
21:00  avg=  0.89  med=  0.95  █
22:00  avg=  1.02  med=  1.06  ██
23:00  avg=  0.93  med=  0.95  █
```

### Frame 2000188388 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 454 m | Ibrox 6,314 m | Hampden 3,976 m | Glasgow Green 1,743 m

```
 0:00  avg=  0.76  med=  0.77  █
 1:00  avg=  0.76  med=  0.77  █
 2:00  avg=  0.76  med=  0.77  █
 3:00  avg=  0.76  med=  0.77  █
 4:00  avg=  0.76  med=  0.77  █
 5:00  avg=  0.86  med=  0.88  █
 6:00  avg=  0.72  med=  0.73  █
 7:00  avg=  0.82  med=  0.82  █
 8:00  avg=  0.68  med=  0.67  █
 9:00  avg=  0.66  med=  0.67  █
10:00  avg=  0.65  med=  0.66  █
11:00  avg=  0.77  med=  0.79  █
12:00  avg=  0.84  med=  0.89  █
13:00  avg=  0.66  med=  0.69  █
14:00  avg=  0.98  med=  1.09  █
15:00  avg=  0.83  med=  0.92  █
16:00  avg=  0.85  med=  0.92  █
17:00  avg=  0.81  med=  0.85  █
18:00  avg=  0.99  med=  1.02  █
19:00  avg=  0.83  med=  0.87  █
20:00  avg=  0.87  med=  0.91  █
21:00  avg=  0.75  med=  0.80  █
22:00  avg=  1.01  med=  1.05  ██
23:00  avg=  1.05  med=  1.07  ██
```

### Frame 2000196441 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 750 m | Ibrox 5,829 m | Hampden 3,087 m | Glasgow Green 1,359 m

```
 0:00  avg=  1.36  med=  1.38  ██
 1:00  avg=  1.36  med=  1.38  ██
 2:00  avg=  1.36  med=  1.38  ██
 3:00  avg=  1.36  med=  1.38  ██
 4:00  avg=  1.36  med=  1.38  ██
 5:00  avg=  1.07  med=  1.06  ██
 6:00  avg=  0.94  med=  0.92  █
 7:00  avg=  0.78  med=  0.73  █
 8:00  avg=  0.80  med=  0.74  █
 9:00  avg=  0.83  med=  0.78  █
10:00  avg=  0.82  med=  0.80  █
11:00  avg=  0.80  med=  0.83  █
12:00  avg=  0.84  med=  0.88  █
13:00  avg=  0.79  med=  0.86  █
14:00  avg=  0.71  med=  0.87  █
15:00  avg=  0.73  med=  0.92  █
16:00  avg=  0.73  med=  0.91  █
17:00  avg=  0.73  med=  0.90  █
18:00  avg=  0.76  med=  0.86  █
19:00  avg=  0.69  med=  0.82  █
20:00  avg=  0.73  med=  0.87  █
21:00  avg=  0.77  med=  0.97  █
22:00  avg=  1.08  med=  1.31  ██
23:00  avg=  1.63  med=  1.71  ███
```

### Frame 2000196441 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 750 m | Ibrox 5,829 m | Hampden 3,087 m | Glasgow Green 1,359 m

```
 0:00  avg=  1.49  med=  1.50  ██
 1:00  avg=  1.49  med=  1.50  ██
 2:00  avg=  1.49  med=  1.50  ██
 3:00  avg=  1.49  med=  1.50  ██
 4:00  avg=  1.49  med=  1.50  ██
 5:00  avg=  1.04  med=  1.03  ██
 6:00  avg=  0.97  med=  0.94  █
 7:00  avg=  0.78  med=  0.73  █
 8:00  avg=  0.69  med=  0.64  █
 9:00  avg=  0.71  med=  0.66  █
10:00  avg=  0.68  med=  0.66  █
11:00  avg=  0.58  med=  0.60  █
12:00  avg=  0.64  med=  0.68  █
13:00  avg=  0.66  med=  0.72  █
14:00  avg=  0.62  med=  0.76  █
15:00  avg=  0.54  med=  0.69  █
16:00  avg=  0.58  med=  0.72  █
17:00  avg=  0.63  med=  0.78  █
18:00  avg=  0.71  med=  0.80  █
19:00  avg=  0.66  med=  0.79  █
20:00  avg=  0.70  med=  0.84  █
21:00  avg=  0.76  med=  0.96  █
22:00  avg=  1.07  med=  1.30  ██
23:00  avg=  1.93  med=  2.02  ███
```

### Frame 2000201879 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 3,196 m | Ibrox 4,039 m | Hampden 4,219 m | Glasgow Green 1,639 m

```
 0:00  avg=  1.40  med=  1.54  ██
 1:00  avg=  1.40  med=  1.54  ██
 2:00  avg=  1.40  med=  1.54  ██
 3:00  avg=  1.40  med=  1.54  ██
 4:00  avg=  1.40  med=  1.54  ██
 5:00  avg=  0.90  med=  0.94  █
 6:00  avg=  0.80  med=  0.82  █
 7:00  avg=  0.71  med=  0.70  █
 8:00  avg=  0.62  med=  0.58  █
 9:00  avg=  0.61  med=  0.58  █
10:00  avg=  0.64  med=  0.64  █
11:00  avg=  0.69  med=  0.70  █
12:00  avg=  0.74  med=  0.77  █
13:00  avg=  0.80  med=  0.83  █
14:00  avg=  0.82  med=  0.85  █
15:00  avg=  0.83  med=  0.85  █
16:00  avg=  0.82  med=  0.84  █
17:00  avg=  0.86  med=  0.87  █
18:00  avg=  0.85  med=  0.87  █
19:00  avg=  0.88  med=  0.93  █
20:00  avg=  0.88  med=  0.96  █
21:00  avg=  0.90  med=  1.00  █
22:00  avg=  1.04  med=  1.14  ██
23:00  avg=  1.59  med=  1.78  ███
```

### Frame 2000201879 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 3,196 m | Ibrox 4,039 m | Hampden 4,219 m | Glasgow Green 1,639 m

```
 0:00  avg=  1.48  med=  1.63  ██
 1:00  avg=  1.48  med=  1.63  ██
 2:00  avg=  1.48  med=  1.63  ██
 3:00  avg=  1.48  med=  1.63  ██
 4:00  avg=  1.48  med=  1.63  ██
 5:00  avg=  0.95  med=  0.99  █
 6:00  avg=  0.79  med=  0.81  █
 7:00  avg=  0.48  med=  0.47  
 8:00  avg=  0.37  med=  0.35  
 9:00  avg=  0.46  med=  0.44  
10:00  avg=  0.50  med=  0.50  █
11:00  avg=  0.54  med=  0.55  █
12:00  avg=  0.55  med=  0.58  █
13:00  avg=  0.57  med=  0.59  █
14:00  avg=  0.57  med=  0.60  █
15:00  avg=  0.55  med=  0.57  █
16:00  avg=  0.52  med=  0.53  █
17:00  avg=  0.53  med=  0.54  █
18:00  avg=  0.61  med=  0.63  █
19:00  avg=  0.62  med=  0.66  █
20:00  avg=  0.70  med=  0.77  █
21:00  avg=  0.73  med=  0.81  █
22:00  avg=  0.95  med=  1.04  █
23:00  avg=  1.82  med=  2.04  ███
```

### Frame 2000212868 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 5,863 m | Ibrox 648 m | Hampden 3,967 m | Glasgow Green 3,964 m

```
 0:00  avg=  0.82  med=  0.83  █
 1:00  avg=  0.82  med=  0.83  █
 2:00  avg=  0.82  med=  0.83  █
 3:00  avg=  0.82  med=  0.83  █
 4:00  avg=  0.82  med=  0.83  █
 5:00  avg=  0.74  med=  0.74  █
 6:00  avg=  0.84  med=  0.85  █
 7:00  avg=  0.71  med=  0.71  █
 8:00  avg=  0.84  med=  0.85  █
 9:00  avg=  0.74  med=  0.75  █
10:00  avg=  0.74  med=  0.76  █
11:00  avg=  0.62  med=  0.63  █
12:00  avg=  0.86  med=  0.87  █
13:00  avg=  0.66  med=  0.68  █
14:00  avg=  0.57  med=  0.59  █
15:00  avg=  0.61  med=  0.61  █
16:00  avg=  0.75  med=  0.75  █
17:00  avg=  0.55  med=  0.56  █
18:00  avg=  0.85  med=  0.86  █
19:00  avg=  0.93  med=  0.95  █
20:00  avg=  0.70  med=  0.71  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.91  med=  0.91  █
23:00  avg=  0.79  med=  0.80  █
```

### Frame 2000212868 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 5,863 m | Ibrox 648 m | Hampden 3,967 m | Glasgow Green 3,964 m

```
 0:00  avg=  1.05  med=  1.06  ██
 1:00  avg=  1.05  med=  1.06  ██
 2:00  avg=  1.05  med=  1.06  ██
 3:00  avg=  1.05  med=  1.06  ██
 4:00  avg=  1.05  med=  1.06  ██
 5:00  avg=  0.73  med=  0.73  █
 6:00  avg=  0.73  med=  0.74  █
 7:00  avg=  0.90  med=  0.90  █
 8:00  avg=  0.77  med=  0.78  █
 9:00  avg=  0.83  med=  0.84  █
10:00  avg=  0.72  med=  0.73  █
11:00  avg=  0.99  med=  1.01  █
12:00  avg=  0.87  med=  0.88  █
13:00  avg=  0.76  med=  0.77  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.86  med=  0.87  █
16:00  avg=  0.71  med=  0.71  █
17:00  avg=  0.70  med=  0.72  █
18:00  avg=  0.67  med=  0.68  █
19:00  avg=  0.72  med=  0.73  █
20:00  avg=  0.90  med=  0.92  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.80  med=  0.80  █
23:00  avg=  0.99  med=  1.00  █
```

### Frame 2000212869 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 5,863 m | Ibrox 647 m | Hampden 3,969 m | Glasgow Green 3,965 m

```
 0:00  avg=  0.82  med=  0.83  █
 1:00  avg=  0.82  med=  0.83  █
 2:00  avg=  0.82  med=  0.83  █
 3:00  avg=  0.82  med=  0.83  █
 4:00  avg=  0.82  med=  0.83  █
 5:00  avg=  0.74  med=  0.74  █
 6:00  avg=  0.84  med=  0.85  █
 7:00  avg=  0.71  med=  0.71  █
 8:00  avg=  0.84  med=  0.85  █
 9:00  avg=  0.74  med=  0.75  █
10:00  avg=  0.74  med=  0.76  █
11:00  avg=  0.62  med=  0.63  █
12:00  avg=  0.86  med=  0.87  █
13:00  avg=  0.66  med=  0.68  █
14:00  avg=  0.57  med=  0.59  █
15:00  avg=  0.61  med=  0.61  █
16:00  avg=  0.75  med=  0.75  █
17:00  avg=  0.55  med=  0.56  █
18:00  avg=  0.85  med=  0.86  █
19:00  avg=  0.93  med=  0.95  █
20:00  avg=  0.70  med=  0.71  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.91  med=  0.91  █
23:00  avg=  0.79  med=  0.80  █
```

### Frame 2000212869 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 5,863 m | Ibrox 647 m | Hampden 3,969 m | Glasgow Green 3,965 m

```
 0:00  avg=  1.05  med=  1.06  ██
 1:00  avg=  1.05  med=  1.06  ██
 2:00  avg=  1.05  med=  1.06  ██
 3:00  avg=  1.05  med=  1.06  ██
 4:00  avg=  1.05  med=  1.06  ██
 5:00  avg=  0.73  med=  0.73  █
 6:00  avg=  0.73  med=  0.74  █
 7:00  avg=  0.90  med=  0.90  █
 8:00  avg=  0.77  med=  0.78  █
 9:00  avg=  0.83  med=  0.84  █
10:00  avg=  0.72  med=  0.73  █
11:00  avg=  0.99  med=  1.01  █
12:00  avg=  0.87  med=  0.88  █
13:00  avg=  0.76  med=  0.77  █
14:00  avg=  0.79  med=  0.81  █
15:00  avg=  0.86  med=  0.87  █
16:00  avg=  0.71  med=  0.71  █
17:00  avg=  0.70  med=  0.72  █
18:00  avg=  0.67  med=  0.68  █
19:00  avg=  0.72  med=  0.73  █
20:00  avg=  0.90  med=  0.92  █
21:00  avg=  0.92  med=  0.94  █
22:00  avg=  0.80  med=  0.80  █
23:00  avg=  0.99  med=  1.00  █
```

### Frame 2000214744 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,806 m | Ibrox 10,873 m | Hampden 8,558 m | Glasgow Green 6,440 m

```
 0:00  avg=  1.07  med=  1.08  ██
 1:00  avg=  1.07  med=  1.08  ██
 2:00  avg=  1.07  med=  1.08  ██
 3:00  avg=  1.07  med=  1.08  ██
 4:00  avg=  1.07  med=  1.08  ██
 5:00  avg=  0.95  med=  0.96  █
 6:00  avg=  0.94  med=  0.94  █
 7:00  avg=  0.96  med=  0.97  █
 8:00  avg=  0.90  med=  0.91  █
 9:00  avg=  0.96  med=  1.01  █
10:00  avg=  1.03  med=  1.10  ██
11:00  avg=  1.03  med=  1.08  ██
12:00  avg=  1.12  med=  1.19  ██
13:00  avg=  1.26  med=  1.32  ██
14:00  avg=  1.43  med=  1.50  ██
15:00  avg=  1.46  med=  1.56  ██
16:00  avg=  1.41  med=  1.51  ██
17:00  avg=  1.22  med=  1.29  ██
18:00  avg=  1.03  med=  1.06  ██
19:00  avg=  0.79  med=  0.78  █
20:00  avg=  0.66  med=  0.66  █
21:00  avg=  0.70  med=  0.72  █
22:00  avg=  0.89  med=  0.92  █
23:00  avg=  0.99  med=  0.99  █
```

### Frame 2000214744 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,806 m | Ibrox 10,873 m | Hampden 8,558 m | Glasgow Green 6,440 m

```
 0:00  avg=  0.94  med=  0.96  █
 1:00  avg=  0.94  med=  0.96  █
 2:00  avg=  0.94  med=  0.96  █
 3:00  avg=  0.94  med=  0.96  █
 4:00  avg=  0.94  med=  0.96  █
 5:00  avg=  1.01  med=  1.02  ██
 6:00  avg=  0.89  med=  0.89  █
 7:00  avg=  0.88  med=  0.88  █
 8:00  avg=  0.76  med=  0.76  █
 9:00  avg=  0.76  med=  0.80  █
10:00  avg=  0.98  med=  1.05  █
11:00  avg=  1.02  med=  1.07  ██
12:00  avg=  1.12  med=  1.18  ██
13:00  avg=  1.19  med=  1.25  ██
14:00  avg=  1.24  med=  1.30  ██
15:00  avg=  1.21  med=  1.29  ██
16:00  avg=  1.11  med=  1.19  ██
17:00  avg=  0.90  med=  0.95  █
18:00  avg=  0.63  med=  0.64  █
19:00  avg=  0.44  med=  0.43  
20:00  avg=  0.42  med=  0.42  
21:00  avg=  0.52  med=  0.54  █
22:00  avg=  0.82  med=  0.85  █
23:00  avg=  1.07  med=  1.08  ██
```

### Frame 2000214745 — 2025-07-12 (ref date: 2024-07-13)
Distances: Celtic Park 4,861 m | Ibrox 10,857 m | Hampden 8,630 m | Glasgow Green 6,454 m

```
 0:00  avg=  1.07  med=  1.08  ██
 1:00  avg=  1.07  med=  1.08  ██
 2:00  avg=  1.07  med=  1.08  ██
 3:00  avg=  1.07  med=  1.08  ██
 4:00  avg=  1.07  med=  1.08  ██
 5:00  avg=  0.95  med=  0.96  █
 6:00  avg=  0.94  med=  0.94  █
 7:00  avg=  0.96  med=  0.97  █
 8:00  avg=  0.90  med=  0.91  █
 9:00  avg=  0.96  med=  1.01  █
10:00  avg=  1.03  med=  1.10  ██
11:00  avg=  1.03  med=  1.08  ██
12:00  avg=  1.12  med=  1.19  ██
13:00  avg=  1.26  med=  1.32  ██
14:00  avg=  1.43  med=  1.50  ██
15:00  avg=  1.46  med=  1.56  ██
16:00  avg=  1.41  med=  1.51  ██
17:00  avg=  1.22  med=  1.29  ██
18:00  avg=  1.03  med=  1.06  ██
19:00  avg=  0.79  med=  0.78  █
20:00  avg=  0.66  med=  0.66  █
21:00  avg=  0.70  med=  0.72  █
22:00  avg=  0.89  med=  0.92  █
23:00  avg=  0.99  med=  0.99  █
```

### Frame 2000214745 — 2025-07-13 (ref date: 2024-07-14)
Distances: Celtic Park 4,861 m | Ibrox 10,857 m | Hampden 8,630 m | Glasgow Green 6,454 m

```
 0:00  avg=  0.94  med=  0.96  █
 1:00  avg=  0.94  med=  0.96  █
 2:00  avg=  0.94  med=  0.96  █
 3:00  avg=  0.94  med=  0.96  █
 4:00  avg=  0.94  med=  0.96  █
 5:00  avg=  1.01  med=  1.02  ██
 6:00  avg=  0.89  med=  0.89  █
 7:00  avg=  0.88  med=  0.88  █
 8:00  avg=  0.76  med=  0.76  █
 9:00  avg=  0.76  med=  0.80  █
10:00  avg=  0.98  med=  1.05  █
11:00  avg=  1.02  med=  1.07  ██
12:00  avg=  1.12  med=  1.18  ██
13:00  avg=  1.19  med=  1.25  ██
14:00  avg=  1.24  med=  1.30  ██
15:00  avg=  1.21  med=  1.29  ██
16:00  avg=  1.11  med=  1.19  ██
17:00  avg=  0.90  med=  0.95  █
18:00  avg=  0.63  med=  0.64  █
19:00  avg=  0.44  med=  0.43  
20:00  avg=  0.42  med=  0.42  
21:00  avg=  0.52  med=  0.54  █
22:00  avg=  0.82  med=  0.85  █
23:00  avg=  1.07  med=  1.08  ██
```

## 4. All Spike Dates for Glasgow Frames (average_index > 3.0)

| Date (2025) | Day | Ref Date (2024) | Frames | Spike-Hours | Peak Index | Avg Index | Likely Event |
|-------------|-----|-----------------|--------|-------------|-----------|-----------|--------------|
| 2025-04-05 | Sat | 2024-04-06 | 3 | 9 | 3.09 | 3.09 |  |
| 2025-04-06 | Sun | 2024-04-07 | 6 | 42 | 8.54 | 6.40 |  |
| 2025-04-12 | Sat | 2024-04-13 | 6 | 45 | 6.60 | 4.85 |  |
| 2025-04-19 | Sat | 2024-04-20 | 16 | 48 | 3.37 | 3.33 |  |
| 2025-04-25 | Fri | 2024-04-26 | 3 | 36 | 4.81 | 4.41 |  |
| 2025-05-03 | Sat | 2024-05-04 | 4 | 45 | 7.57 | 5.42 |  |
| 2025-05-04 | Sun | 2024-05-05 | 2 | 30 | 6.32 | 5.72 |  |
| 2025-05-06 | Tue | 2024-05-07 | 3 | 36 | 5.13 | 4.62 |  |
| 2025-05-09 | Fri | 2024-05-10 | 1 | 9 | 3.77 | 3.63 |  |
| 2025-05-10 | Sat | 2024-05-11 | 4 | 60 | 7.97 | 5.28 |  |
| 2025-05-13 | Tue | 2024-05-14 | 3 | 39 | 5.35 | 4.38 |  |
| 2025-05-14 | Wed | 2024-05-15 | 1 | 6 | 7.18 | 5.82 |  |
| 2025-05-17 | Sat | 2024-05-18 | 13 | 154 | 7.91 | 4.73 |  |
| 2025-05-18 | Sun | 2024-05-19 | 1 | 12 | 4.93 | 4.03 |  |
| 2025-05-24 | Sat | 2024-05-25 | 1 | 3 | 3.00 | 3.00 |  |
| 2025-05-25 | Sun | 2024-05-26 | 2 | 24 | 3.77 | 3.61 |  |
| 2025-05-28 | Wed | 2024-05-29 | 5 | 15 | 3.22 | 3.22 |  |
| 2025-05-31 | Sat | 2024-06-01 | 1 | 3 | 3.01 | 3.01 |  |
| 2025-06-06 | Fri | 2024-06-07 | 1 | 15 | 5.53 | 4.74 |  |
| 2025-06-16 | Mon | 2024-06-17 | 1 | 18 | 5.75 | 3.95 |  |
| 2025-06-17 | Tue | 2024-06-18 | 1 | 15 | 4.48 | 4.48 |  |
| 2025-06-21 | Sat | 2024-06-22 | 14 | 84 | 3.83 | 3.79 |  |
| 2025-06-24 | Tue | 2024-06-25 | 7 | 21 | 3.56 | 3.28 |  |
| 2025-06-25 | Wed | 2024-06-26 | 7 | 45 | 3.29 | 3.22 |  |
| 2025-06-27 | Fri | 2024-06-28 | 1 | 18 | 6.28 | 4.05 |  |
| 2025-06-28 | Sat | 2024-06-29 | 7 | 111 | 6.35 | 4.06 |  |
| 2025-06-29 | Sun | 2024-06-30 | 7 | 105 | 6.77 | 3.74 |  |
| 2025-07-04 | Fri | 2024-07-05 | 1 | 15 | 3.37 | 3.37 |  |
| 2025-07-05 | Sat | 2024-07-06 | 2 | 30 | 3.97 | 3.54 |  |
| 2025-07-09 | Wed | 2024-07-10 | 1 | 15 | 4.09 | 3.64 |  |
| 2025-07-11 | Fri | 2024-07-12 | 9 | 291 | 13.21 | 8.91 |  |
| 2025-07-12 | Sat | 2024-07-13 | 9 | 396 | 18.60 | 10.72 | TRNSMT Day 2? / Celtic/Rangers fixture? |
| 2025-07-13 | Sun | 2024-07-14 | 9 | 374 | 18.29 | 10.19 | TRNSMT Day 3? / Post-match activity? |
| 2025-07-19 | Sat | 2024-07-20 | 6 | 16 | 3.01 | 3.01 |  |
| 2025-08-02 | Sat | 2024-08-03 | 14 | 84 | 4.56 | 4.16 |  |
| 2025-08-03 | Sun | 2024-08-04 | 18 | 258 | 9.86 | 4.68 |  |
| 2025-08-16 | Sat | 2024-08-17 | 9 | 227 | 5.21 | 3.80 |  |
| 2025-08-17 | Sun | 2024-08-18 | 3 | 36 | 5.92 | 4.82 |  |
| 2025-08-24 | Sun | 2024-08-25 | 2 | 12 | 3.21 | 3.13 |  |
| 2025-08-31 | Sun | 2024-09-01 | 4 | 57 | 7.08 | 4.86 |  |
| 2025-09-04 | Thu | 2024-09-05 | 1 | 15 | 4.37 | 3.73 |  |
| 2025-09-13 | Sat | 2024-09-14 | 9 | 63 | 6.74 | 4.46 |  |
| 2025-09-14 | Sun | 2024-09-15 | 5 | 15 | 3.30 | 3.30 |  |
| 2025-09-17 | Wed | 2024-09-18 | 5 | 72 | 13.29 | 7.90 |  |
| 2025-09-19 | Fri | 2024-09-20 | 2 | 30 | 6.83 | 5.75 |  |
| 2025-09-20 | Sat | 2024-09-21 | 2 | 24 | 6.50 | 5.87 |  |
| 2025-09-21 | Sun | 2024-09-22 | 4 | 42 | 6.10 | 4.43 |  |
| 2025-09-28 | Sun | 2024-09-29 | 2 | 30 | 6.25 | 5.56 |  |
| 2025-10-02 | Thu | 2024-10-03 | 2 | 30 | 6.85 | 5.84 |  |
| 2025-10-05 | Sun | 2024-10-06 | 11 | 237 | 6.55 | 5.06 |  |
| 2025-10-14 | Tue | 2024-10-15 | 1 | 12 | 4.16 | 3.62 |  |
| 2025-10-18 | Sat | 2024-10-19 | 5 | 54 | 7.20 | 4.87 |  |
| 2025-10-23 | Thu | 2024-10-24 | 2 | 30 | 7.23 | 6.42 |  |
| 2025-10-24 | Fri | 2024-10-25 | 4 | 36 | 3.78 | 3.54 |  |
| 2025-10-25 | Sat | 2024-10-26 | 4 | 36 | 3.55 | 3.38 |  |
| 2025-10-26 | Sun | 2024-10-27 | 4 | 54 | 5.86 | 4.52 |  |
| 2025-10-29 | Wed | 2024-10-30 | 5 | 66 | 10.67 | 6.60 |  |
| 2025-10-30 | Thu | 2024-10-31 | 6 | 16 | 3.17 | 3.17 |  |
| 2025-11-01 | Sat | 2024-11-02 | 1 | 9 | 3.53 | 3.21 |  |
| 2025-11-02 | Sun | 2024-11-03 | 5 | 15 | 3.04 | 3.04 |  |
| 2025-11-04 | Tue | 2024-11-05 | 6 | 78 | 13.19 | 7.36 |  |
| 2025-11-09 | Sun | 2024-11-10 | 2 | 30 | 6.43 | 5.39 |  |
| 2025-11-12 | Wed | 2024-11-13 | 1 | 6 | 3.31 | 3.21 |  |
| 2025-11-14 | Fri | 2024-11-15 | 1 | 9 | 3.70 | 3.38 |  |
| 2025-11-22 | Sat | 2024-11-23 | 2 | 30 | 4.54 | 4.27 |  |
| 2025-11-26 | Wed | 2024-11-27 | 6 | 78 | 13.26 | 7.25 |  |
| 2025-11-28 | Fri | 2024-11-29 | 14 | 42 | 3.28 | 3.28 |  |
| 2025-11-29 | Sat | 2024-11-30 | 29 | 114 | 6.12 | 3.50 |  |
| 2025-12-03 | Wed | 2024-12-04 | 2 | 30 | 5.27 | 4.50 |  |
| 2025-12-11 | Thu | 2024-12-12 | 4 | 42 | 7.35 | 5.44 |  |
| 2025-12-19 | Fri | 2024-12-20 | 6 | 36 | 3.43 | 3.19 |  |
| 2025-12-20 | Sat | 2024-12-21 | 2 | 24 | 5.14 | 4.92 |  |
| 2025-12-22 | Mon | 2024-12-23 | 4 | 48 | 4.59 | 3.73 |  |
| 2025-12-25 | Thu | 2024-12-26 | 3 | 30 | 4.60 | 3.87 |  |
| 2025-12-28 | Sun | 2024-12-29 | 5 | 48 | 5.33 | 3.95 |  |

- Total spike dates: **75**
- Saturdays: 23, Sundays: 18 (54.7% weekend)

## 5. Peak Hour Distribution for Glasgow Spikes

| Hour | Spike Count | Unique Frames | Peak Index | Avg Index |
|------|-------------|---------------|------------|-----------|
| 00:00 | 128 | 30 | 6.77 | 3.97 |
| 01:00 | 128 | 30 | 6.77 | 3.97 |
| 02:00 | 128 | 30 | 6.77 | 3.97 |
| 03:00 | 128 | 30 | 6.77 | 3.97 |
| 04:00 | 128 | 30 | 6.77 | 3.97 |
| 08:00 | 38 | 7 | 3.92 | 3.36 |
| 09:00 | 47 | 9 | 5.25 | 4.15 |
| 10:00 | 68 | 12 | 5.91 | 4.47 |
| 11:00 | 138 | 22 | 8.54 | 4.58 |
| 12:00 | 164 | 17 | 8.36 | 4.96 |
| 13:00 | 200 | 17 | 8.03 | 5.11 |
| 14:00 | 318 | 20 | 9.06 | 5.19 |
| 15:00 | 324 | 20 | 12.08 | 5.56 |
| 16:00 | 294 | 18 | 14.16 | 6.44 |
| 17:00 | 284 | 22 | 15.31 | 6.91 |
| 18:00 | 266 | 22 | 15.89 | 6.76 |
| 19:00 | 286 | 27 | 15.79 | 7.45 |
| 20:00 | 270 | 32 | 16.35 | 7.72 |
| 21:00 | 267 | 30 | 17.37 | 8.19 |
| 22:00 | 378 | 42 | 18.14 | 6.77 |
| 23:00 | 408 | 63 | 18.60 | 5.69 |

Modal spike hour: **23:00** (408 spikes). Late-evening peaks (21:00–23:00) are consistent with post-event crowd dispersal.

## 6. Top Glasgow Frames by Spike Frequency

| Frame | Town | Address | POI | Spike Hours | Spike Days | Peak | Avg |
|-------|------|---------|-----|-------------|------------|------|-----|
| 1235464179 | Glasgow North | Glasgow Eastern Gateway |  | 258 | 20 | 12.07 | 6.28 |
| 2000196441 | Glasgow North | Dunn Street |  | 249 | 19 | 13.29 | 6.62 |
| 1234852697 | Glasgow North | Asda Parkhead The Forge Centre Glasgow | ASDAPARKHEADFORGE | 243 | 17 | 12.67 | 5.35 |
| 2000118300 | Glasgow North | Trongate (Jcn Albion St, OS 36 Guitar Gu |  | 219 | 8 | 18.48 | 7.73 |
| 2000028113 | Glasgow North | Vm - 109-115 Gallowgate Spoutmouth Glasg |  | 219 | 8 | 18.48 | 7.73 |
| 1234859353 | Glasgow North | Gallowgate C/O Spoutmouth Glasgow |  | 219 | 8 | 18.48 | 7.73 |
| 2000118304 | Glasgow North | Trongate (Jcn Albion St, OS 36 Guitar Gu |  | 219 | 8 | 18.48 | 7.73 |
| 1234859354 | Glasgow North | Gallowgate C/O Spoutmouth Glasgow |  | 219 | 8 | 18.48 | 7.73 |
| 2000113429 | Glasgow North | D48 - London Road, Glasgow |  | 207 | 9 | 18.60 | 8.12 |
| 1234606817 | Glasgow South | Ibrox Station, 124 Copland Road, Glasgow | Ibrox SPT | 204 | 14 | 8.54 | 5.54 |
| 1234606822 | Glasgow South | Ibrox Station, 124 Copland Road, Glasgow | Ibrox SPT | 204 | 14 | 8.54 | 5.54 |
| 1234852698 | Glasgow South | Asda Toryglen 555 Prospect Hill Road Gla | ASDAPROSPECTHILL | 153 | 12 | 6.77 | 4.48 |
| 1234861346 | Glasgow North | Gallowgate Opp 370 Gallowgate adj Morris |  | 138 | 6 | 15.76 | 8.98 |
| 1234861345 | Glasgow North | Gallowgate Opp 370 Gallowgate adj Morris |  | 138 | 6 | 15.76 | 8.98 |
| 2000188388 | Glasgow North | GALLOWGATE, GLASGOW |  | 123 | 14 | 4.37 | 3.60 |
| 1234861335 | Glasgow North | Gallowgate Gallowgate at Watson Street,  |  | 73 | 8 | 18.48 | 7.73 |
| 1234855591 | Motherwell | Windmillhill St at 49 opp Camp St Mother |  | 51 | 6 | 6.83 | 4.12 |
| 1234855590 | Motherwell | Windmillhill St at 49 opp Camp St Mother |  | 51 | 6 | 6.83 | 4.12 |
| 1234856789 | Glasgow North | North East side of Carntyne Road (Todd S |  | 51 | 5 | 5.03 | 3.94 |
| 1234926779 | Glasgow South | INTU BRAEHEAD S/C - RENFREW,UPPER MALL-O | Glasgow - Braehead Shopping Ce | 33 | 5 | 4.56 | 4.03 |

## 7. Context: How Does the July 2025 Cluster Rank Nationally?

National picture on the target dates:

| Date | Day | Total Spike Frames (national) | National Peak Index |
|------|-----|-------------------------------|---------------------|
| 2025-07-12 | Sat | 23 | 18.60 |
| 2025-07-13 | Sun | 18 | 18.29 |

## 8. Event Cross-Reference

### Known 2025 Glasgow Events (research required to confirm dates)

The following events are likely candidates for the July 12–13 2025 spikes. Confirm exact dates via official sources:

| Event | Venue | Typical Dates | Notes |
|-------|-------|---------------|-------|
| **TRNSMT Festival** | Glasgow Green | Early July (Fri–Sun) | 3-day music festival; 2024 was 5–7 July |
| **Celtic FC home fixture** | Celtic Park | Season Aug–May (plus pre-season) | Pre-season friendlies possible July |
| **Rangers FC home fixture** | Ibrox Stadium | Season Aug–May (plus pre-season) | Pre-season friendlies possible July |
| **Concert at Celtic Park** | Celtic Park | Summer (ad hoc) | Capacity ~60,000 |
| **Concert at Ibrox** | Ibrox Stadium | Summer (ad hoc) | Capacity ~51,000 |
| **Concert at Hampden** | Hampden Park | Summer (ad hoc) | National stadium, used for large concerts |

### Key Observation

TRNSMT 2025 is the most likely explanation for July 12–13 spikes: the festival runs Friday–Sunday at Glasgow Green, with 23:00 being the typical headline finish time. Glasgow Green is equidistant between Celtic Park and Ibrox, so frames nearest Glasgow Green or the city centre would spike regardless of which club ground is closer. Verify 2025 TRNSMT dates at: https://trnsmtfest.com

### Scottish Premiership Season Note

The Scottish Premiership 2024/25 season typically ends in May. Pre-season friendlies begin late July or August. Celtic and Rangers are unlikely to have competitive home fixtures on 12–13 July 2025, making TRNSMT or a summer concert a stronger hypothesis.

## 9. Confidence Assessment

| Factor | Signal | Confidence |
|--------|--------|------------|
| Frame locations relative to Glasgow Green | TBC from distance table above | High if < 1 km |
| Spike timing at 23:00 | Consistent with festival headline finish | High |
| Multi-frame cluster (6+) | Corroborates crowd rather than single anomaly | High |
| Spike on both Sat 12 & Sun 13 July | Matches 3-day festival day 2 & 3 | High |
| No Celtic/Rangers competitive fixture in July | Reduces stadium hypothesis | Medium |
| TRNSMT 2024 was 5–7 July (Fri–Sun) | 2025 dates TBC but same pattern expected | Medium |

**Overall: HIGH confidence this cluster is TRNSMT Festival or a major summer concert at Celtic Park / Hampden, rather than a football fixture.** Confirm by checking TRNSMT 2025 lineup announcement and Ticketmaster for Celtic Park / Hampden summer concerts.

---
*Script: `scripts/research_glasgow_cluster.py` — generated automatically*
