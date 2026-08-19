# autoBovina standalone

**VIF: DA, dar numai mock în această versiune**

Este varianta reconstruită și distribuibilă a aplicației `autoBovina`.
Validează registrul Excel și reproduce pașii recuperați ai fluxurilor VIF
`p01` și `p02` sub forma unui transcript controlat.

## Ce face

- citește `data/settings.txt`;
- validează structura și valorile din registrul Excel;
- pregătește pașii de recepție și sincronizare pentru bovine;
- înregistrează interacțiunile Putty într-un adaptor mock.

## Limită importantă

Distribuția nu pornește Putty și nu trimite date către VIF. Executabilul din
`dist/` și installerul din `release/` sunt pentru rulare locală, cu setări
configurate explicit.
