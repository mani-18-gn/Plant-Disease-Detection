# PlantGuard — Agricultural Resources & Verified Knowledge Base

## 1. Public Agricultural Research Institutions (India & International)

This platform builds upon verified agricultural research, peer-reviewed plant pathology literature, and official packages of practices published by Indian agricultural institutions and international bodies.

### Indian Council of Agricultural Research (ICAR) & National Institutes
* **ICAR-IIHR (Indian Institute of Horticultural Research, Bengaluru)**:
  * Research focus: Tomato, Chilli, Brinjal, Mango, Banana, Papaya disease management.
  * Verified protocols: Bio-fungicide spray schedules (*Trichoderma harzianum*, *Pseudomonas fluorescens*), IPM packages for Late Blight, Leaf Curl, and Bacterial Wilt.
  * Official Portal: [https://iihr.icar.gov.in](https://iihr.icar.gov.in)
* **ICAR-CPRI (Central Potato Research Institute, Shimla)**:
  * Research focus: Potato pathology (*Phytophthora infestans* Late Blight, *Alternaria solani* Early Blight, Viral degenerations).
  * Decision support: INDO-BLIGHTCAST late blight forecasting model and CIBRC-approved fungicide schedules.
  * Official Portal: [https://cpri.icar.gov.in](https://cpri.icar.gov.in)
* **ICAR-CPCRI (Central Plantation Crops Research Institute, Kasaragod)**:
  * Research focus: Arecanut (*Areca catechu*) and Coconut (*Cocos nucifera*).
  * Major diseases: Koleroga / Mahali (Fruit rot - *Phytophthora meadii*), Yellow Leaf Disease (Phytoplasma), Stem Bleeding (*Thielaviopsis paradoxa*), Anabe / Foot rot (*Ganoderma lucidum*).
  * Official Portal: [https://cpcri.icar.gov.in](https://cpcri.icar.gov.in)
* **ICAR-IARI (Indian Agricultural Research Institute, Pusa, New Delhi)**:
  * Focus: Cereal pathology (Wheat rusts, Karnal bunt, Rice blast, Maize leaf blights).
  * Official Portal: [https://iari.res.in](https://iari.res.in)
* **ICAR-SBI (Sugarcane Breeding Institute, Coimbatore)**:
  * Focus: Sugarcane red rot (*Colletotrichum falcatum*), smut, and ratoon stunting.
  * Official Portal: [https://sugarcane.icar.gov.in](https://sugarcane.icar.gov.in)

### State Agricultural Universities (SAUs)
* **University of Agricultural Sciences, Bangalore (UASB - GKVK)**:
  * *Package of Practices for Horticultural and Field Crops of Southern Karnataka* (Bilingual: Kannada & English).
  * Crop guidance: Arecanut, Maize, Tomato, Chilli, Ragi, Pulses.
  * Official Portal: [https://uasbangalore.edu.in](https://uasbangalore.edu.in)
* **University of Agricultural Sciences, Dharwad (UASD)**:
  * Northern Karnataka agrarian zone guidance: Cotton, Chilli (Byadgi), Soybean, Bengal gram.
  * Official Portal: [https://uasd.edu](https://uasd.edu)
* **Tamil Nadu Agricultural University (TNAU Agritech Portal)**:
  * Highly granular, open-access diagnostic keys for agricultural crops, symptoms, differential diagnoses, and IPM measures.
  * Official Portal: [https://agritech.tnau.ac.in](https://agritech.tnau.ac.in)
* **Punjab Agricultural University (PAU, Ludhiana)** & **Kerala Agricultural University (KAU)**:
  * Regional wheat, rice, and plantation crop pathology compendia.

### Krishi Vigyan Kendras (KVKs) & Extension Machinery
* Over 730 district-level KVKs funded by ICAR serve as front-line technology transfer and physical diagnostic centers.
* **Platform Protocol**: All automated model inferences are presented as decision-support aids; physical confirmation by KVK agronomists is flagged as mandatory prior to applying Schedule IV chemical fungicides.
* Extension Portal: [https://kvk.icar.gov.in](https://kvk.icar.gov.in) / [https://farmer.gov.in](https://farmer.gov.in)

### International Agricultural Repositories
* **Food and Agriculture Organization (FAO) of the United Nations**:
  * FAO Plant Production and Protection Papers, Integrated Pest Management guidelines, Fall Armyworm and Citrus Greening (HLB) international containment protocols.
  * Official Portal: [https://www.fao.org/agriculture](https://www.fao.org/agriculture)
* **CABI Plantwise Knowledge Bank & Compendium**:
  * Global open access diagnostic guides, pest distribution maps, and biological control datasheets.
  * Official Portal: [https://www.plantwise.org](https://www.plantwise.org)

---

## 2. Benchmark Datasets & Legal Compliance

| Dataset Name | Origin / Authors | License / Access Terms | Crops Covered | Target Classes | Utilization in Platform |
|---|---|---|---|---|---|
| **PlantVillage** | Penn State University (Hughes & Salathé, 2015) | Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0) | 14 crops (Tomato, Potato, Pepper, Corn, Apple, Grape, Citrus, Peach, Strawberry, Cherry, Blueberry, Squash, Soybean, Raspberry) | 38 disease & healthy categories (54,303 images) | Primary visual classifier backbone (MobileNetV2 fine-tuned) |
| **PlantDoc** | IIT Delhi (Singh, Anand, et al., 2020) | Open Academic Research / arXiv:1911.10314 | 13 plant species in real outdoor field contexts | 27 classes (2,598 field images) | Robustness evaluation & real-world field symptom verification |
| **CPCRI Arecanut Pathology Archive** | ICAR-CPCRI Kasaragod / Regional Extension | Official Public Advisory Compendia | Arecanut (*Areca catechu*) | 5 conditions (Koleroga, Yellow Leaf, Bud Borer, Stem Bleeding, Healthy) | Agronomic advisory, differential diagnosis, and Bayesian posterior engine |
| **TNAU Crop Protection Keys** | TNAU Agritech Portal | Public Extension Educational Resource | Rice, Cotton, Sugarcane, Banana, Mango, Pulses | 40+ regional tropical diseases | Extended agronomic advisory database & differential diagnosis keys |

### Compliance Principles:
1. **Explicit Licensing**: We only utilize checkpoints trained on publicly released, open-licensed datasets (CC BY-SA 4.0 / Open Academic Research).
2. **No Arbitrary Scraping**: We do NOT scrape copyrighted commercial stock photos, paywalled journals, or private farm portals.
3. **No Synthetic Misrepresentation**: Softmax probabilities are strictly reported as model activations, never fabricated or inflated.
4. **Transparent Crop Bounds**: Classes outside the trained 38-class MobileNetV2 vision weights are explicitly routed to agronomic advisory keys and labeled as "Extended Advisory / Visual Classifier Not Yet Fine-Tuned".

---

## 3. Supported Crops & Scientific Taxonomies

### A. Field & Vegetable Crops (Visual Model Supported)
1. **Tomato (*Solanum lycopersicum*)**:
   * Bacterial Spot (*Xanthomonas campestris pv. vesicatoria*)
   * Early Blight (*Alternaria solani*)
   * Late Blight (*Phytophthora infestans*)
   * Leaf Mold (*Passalora fulva*)
   * Septoria Leaf Spot (*Septoria lycopersici*)
   * Spider Mites (*Tetranychus urticae*)
   * Target Spot (*Corynespora cassiicola*)
   * Tomato Yellow Leaf Curl Virus (TYLCV - Begomovirus transmitted by *Bemisia tabaci*)
   * Tomato Mosaic Virus (ToMV - Tobamovirus)
   * Healthy Foliage
2. **Potato (*Solanum tuberosum*)**:
   * Early Blight (*Alternaria solani*)
   * Late Blight (*Phytophthora infestans*)
   * Healthy Foliage
3. **Chilli / Bell Pepper (*Capsicum annuum*)**:
   * Bacterial Spot (*Xanthomonas euvesicatoria*)
   * Healthy Foliage
4. **Corn / Maize (*Zea mays*)**:
   * Common Rust (*Puccinia sorghi*)
   * Northern Leaf Blight (*Exserohilum turcicum*)
   * Gray Leaf Spot (*Cercospora zeae-maydis*)
   * Healthy Foliage
5. **Grape (*Vitis vinifera*)**:
   * Black Rot (*Guignardia bidwellii*)
   * Esca / Black Measles (*Fomitiporia mediterranea / Phaeomoniella*)
   * Leaf Blight / Isariopsis Leaf Spot (*Pseudocercospora cladosporioides*)
   * Healthy Foliage
6. **Apple (*Malus domestica*)**:
   * Apple Scab (*Venturia inaequalis*)
   * Black Rot (*Botryosphaeria obtusa*)
   * Cedar Apple Rust (*Gymnosporangium juniperi-virginianae*)
   * Healthy Foliage
7. **Citrus / Orange (*Citrus sinensis*)**:
   * Citrus Greening / Huanglongbing (*Candidatus Liberibacter asiaticus*)
8. **Peach, Strawberry, Cherry, Squash, Soybean, Blueberry, Raspberry**:
   * Powdery Mildew, Leaf Scorch, Bacterial Spot, and Healthy states.

### B. Extended Indian Plantation & Cash Crops (Agronomic & Differential Advisory)
1. **Arecanut (*Areca catechu*)**:
   * Mahali / Koleroga (*Phytophthora meadii*)
   * Yellow Leaf Disease (Phytoplasma transmitted by *Proutista moesta*)
   * Bud Borer (*Tirathaba mundella*)
   * Stem Bleeding (*Thielaviopsis paradoxa*)
   * Healthy Palm
2. **Rice (*Oryza sativa*)**:
   * Blast (*Magnaporthe oryzae*)
   * Bacterial Leaf Blight (*Xanthomonas oryzae pv. oryzae*)
   * Brown Spot (*Bipolaris oryzae*)
   * Sheath Blight (*Rhizoctonia solani*)
3. **Cotton (*Gossypium hirsutum*)**:
   * Bacterial Blight / Black Arm (*Xanthomonas citri pv. malvacearum*)
   * Cotton Leaf Curl Virus (CLCuV)
4. **Sugarcane (*Saccharum officinarum*)**:
   * Red Rot (*Colletotrichum falcatum*)
5. **Mango (*Mangifera indica*)**:
   * Anthracnose (*Colletotrichum gloeosporioides*)
6. **Banana (*Musa acuminata*)**:
   * Sigatoka Leaf Spot (*Pseudocercospora fijiensis*)

---

## 4. Legal & Agronomic Safety Protocols
1. **Central Insecticides Board & Registration Committee (CIBRC)**: All chemical management recommendations reference legally permitted active ingredients in India with prescribed dosages and Pre-Harvest Intervals (PHI).
2. **Strict Advisory Disclaimer**: The platform prominently states that visual deep learning models cannot replace on-ground laboratory culturing, PCR assays, or physical diagnostic inspection by certified plant pathologists.
