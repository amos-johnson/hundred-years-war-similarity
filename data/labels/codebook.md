# Article types: codebook

Draft for Amos to edit. One label per article: **what kind of thing the article is about**, not how it relates to the war. The seed (*Hundred Years' War*) is left unlabeled: it's the reference point, not a member of any theme.

| Label | The article is about… | Examples |
|---|---|---|
| battles and sieges | a single engagement: a battle, siege or skirmish | Battle of Crécy, Siege of Meaux |
| wars and campaigns | a conflict or campaign made of several engagements, including invasions and military operations | Gascon War, Loire Campaign (1429), Reconquista, Operation Torch |
| historical people | a person who lived in or shaped the period's history | Edward III, Joan of Arc, Jean Fouquet |
| dynasties and polities | a state, royal house or noble family, or the history of one | House of Valois, Crown of Castile, Percy family |
| places | a city, region or territory | Calais, Agenais, Pale of Calais |
| events and treaties | a non-battle event: treaty, truce, alliance, revolt, trial, diplomatic incident, claim to a throne | Treaty of Brétigny, Peasants' Revolt, Fashoda Incident |
| military concepts and technology | a weapon, unit, tactic or type of warfare | English longbow, Artillery, Privateer, Proxy war |
| institutions, titles and concepts | a title, office, legal or social institution, or principle | Baron, Fief, Chivalry, Medieval university |
| periods, culture and religion | an era, cultural field, religion, ideology or intellectual movement | Middle Ages, Medieval music, East–West Schism, French nationalism |
| scholarship and media | modern scholarship and works about the past: historians, publishers, journals, archives, films, plays, operas | Desmond Seward, Speculum (journal), Joan the Woman |
| other | none of the above (nature, disease, articles about a name…) | Hail, Dysentery, Name of Joan of Arc |

## Rules for edge cases
- **Battle vs war:** one engagement → battles and sieges; several → wars and campaigns. A named incident without fighting (Fashoda, Nootka, Levant Crisis) → events and treaties.
- **People vs scholarship:** historians, authors and scientists writing *about* the past → scholarship and media, even when the article is a biography (Peter Turchin, Christopher Allmand).
- **Places vs polities:** a territory defined by geography or administration → places (Pale of Calais, Gascony); a state, kingdom or dynasty with its own rulers → dynasties and polities (Crown of Castile).
- **"History of X"** takes X's type (History of the European Union → dynasties and polities).
- **Periods and crises** (Middle Ages, Crisis of the Third Century, Crisis of the late Middle Ages) → periods, culture and religion, not events.
- **Works about a person or event** (films, plays, operas) → scholarship and media, not the subject's type (The Trial of Joan of Arc at Rouen, 1431 is Brecht's play).
- **Pandemics and diseases** (Black Death, Plague (disease), COVID-19 pandemic in Europe) → other, consistent with the first labels.
- **Revolts:** with armed fighting over months (Revolt of 1173–1174, Welsh uprising of 1211) → wars and campaigns; a short uprising (Peasants' Revolt) stays in events and treaties.
- **Lists and bibliographies** take the type of what they list (List of English monarchs → historical people, List of Anglo-Welsh wars → wars and campaigns); a bibliography → scholarship and media.
- **Topics about one aspect of a person** (Name of Joan of Arc, Cross-dressing… of Joan of Arc) → other; **depictions in culture** (Cultural depictions of Joan of Arc, Middle Ages in popular culture) → scholarship and media.
- **Relations, disputes and affairs between states or in a court** (France–United Kingdom relations, 2021 Jersey dispute, Tour de Nesle affair) → events and treaties.
- **Economy and language** have no category of their own: Medieval English wool trade and Influence of French on English → periods, culture and religion.
- **Revolutions and long-run historical processes** (French Revolution, Great Divergence, Christianization) → periods, culture and religion.

## Who labeled what
`labels.csv` has a `source` column: **Amos (random sample)**, 199 articles, the only ones used to estimate accuracy; **Claude (round 1, uncertain articles)**, 50 articles the model was least sure about, labeled with this codebook on 24 Nov 2026 and approved by Amos, including the 14 doubtful calls marked `unsure` in `to_label_round1.csv`.

## Changes from the first labels (24 Nov 2026)
Original labels are kept in `labels_original.csv`. "battles" was split into battles and sieges vs wars and campaigns; "institutions and society" into institutions, titles and concepts vs periods, culture and religion; films, incidents and periods moved out of "other"; biography → historical people, with modern scholars moved to scholarship and media; the seed's label removed.
