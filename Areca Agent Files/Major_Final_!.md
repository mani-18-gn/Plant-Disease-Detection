# **ARECA AGENT** 



### **A PROJECT REPORT– PHASE 1** 

##### **Submitted to** 

### **Visvesvaraya Technological University BELAGAVI - 590 018** 

##### **by** 

**Samarth N K Sathwik Hebbar P Suchesh S Shetty Vihar A C** 

**4SU23CS083 4SU23CS088 4SU23CS102 4SU23CS122** 

###### **Under the guidance of** 

##### **Dr Thyagaraju G S** 

**Prof and Head Of Department** 

**in partial fulfillment of the requirements for the award of the degree of** 

### **Bachelor of Engineering** 





**Department of Computer Science & Engineering SDM INSTITUTE OF TECHNOLOGY UJIRE - 574 240 2025-2026** 

## **SDM INSTITUTE OF TECHNOLOGY** 

(Affiliated to Visvesvaraya Technological University, Belagavi) 

**UJIRE – 574 240** 

**Department of Computer Science and Engineering** 

**_<u>CERTIFICATE</u>_** Certified that the Project Work titled ‘ **Areca Agent** ’ is being carried out by **Mr. Samarth N K** , USN: **4SU23CS083, Mr. Sathwik Hebbar P** , USN: **4SU23CS088, Mr. Suchesh.S.Shetty** , USN: **4SU23CS102, Mr. Vihar A C** , USN: **4SU23CS122,** bonafide students of SDM Institute of Technology, Ujire, in partial fulfillment for the award of the degree of **Bachelor of Engineering** in Computer Science and Engineering of Visvesvaraya Technological University, Belagavi during the year 2025-2026. It is certified that all the corrections/suggestions indicated for Internal Assessment have been incorporated in the report deposited in the departmental library. The report has been approved as it satisfies the academic requirements in respect of project work prescribed for the said Degree. **Mr.Pradeep Rao K B                                                        Dr. Thyagaraju G S** Asst. Professor and Project Coordinator                                   Professor,Guide And Head Of Dept 

### **Acknowledgement** 

### **________________________________________________** 

It is our pleasure to express our heartfelt thanks to Dr.Thyagaraju G S, Head Of Department ,Department of Computer Science and Engineering, for his supervision and guidance. 

We are indebted to Dr. Ashok Kumar T, Principal, for his advice and suggestions at various stages of the work. We also extend our heartfelt gratitude to Mr. Pradeep Rao K B, Project Coordinator for his assistance and the management of SDM Institute of Technology, Ujire, for providing us with a good learning environment, library and laboratory facilities. 

Lastly, we take this opportunity to offer our regards to all of those who have supported us directly or indirectly in the successful completion of the Project Phase 1. 

Samarth N K 

Sathwik Hebbar P Suchesh.S.Shetty 

Vihar A C 

### **Abstract** 

Arecanut cultivation is a vital part of the agricultural economy in regions like Karnataka, Kerala, and Assam, but farmers face challenges such as delayed disease detection, climate uncertainty, and unstable market prices. Traditional methods often lead to inefficient decision-making, increased costs, and reduced yield. To address these issues, this project proposes Areca Agent, a multi-agent AI-based crop monitoring and decision-support system. 

The system integrates specialized agents for disease detection using CNN, weather analysis, market prediction, and intelligent advisory generation. A central coordinator agent manages communication between agents to deliver accurate, context-aware recommendations. It also incorporates real-time data, historical records, and user feedback for continuous improvement. 

By combining artificial intelligence, real-time analytics, and predictive modeling, Areca Agent enables early disease detection, better resource management, and informed market decisions. This approach enhances productivity, reduces costs, and supports sustainable arecanut farming. 

i 

### **Table of Contents** 

|||**Page No.**|
|---|---|---|
|**Abstract**||**i**|
|**Table of Con**|**tents**|**ii**|
|**List of Figur**|**es**|**iii**|
|**List of Table**|**s**|**iv**|
|**Chapter 1**|**Introduction**|**1**|
|1.1|Project Introduction|1|
|1.2|Problem Description|2|
|**Chapter 2**|**Literature Review**|**3**|
|2.1|Literature Survey|3|
|2.2|Comparative Analysis of the Related Work|11|
|2.3|Summary|13|
|**Chapter 3**|**Problem Formulation**|**14**|
|3.1|Problem Statement|14|
|3.2|Objectives of the Present Study|14|
|3.3|Summary|14|
|**Chapter 4**|**Requirements and Methodology**|**16**|
|4.1|Hardware Requirements|16|
|4.2|Software Requirements|16|
|4.3|Datasets Required|16|
|4.4|Algorithms Required|17|
|4.5|Methodology|21|
|**Chapter 5**|**System Design**|**24**|
|5.1|Architecture of the Proposed System|24|
|5.2|System Flowchart|25|
|5.3|User Interface Design|26|
|**Chapter 6**|**Conclusion**|**29**|
|**Chapter 7**|**Plan for Completion of Pending Work**|**30**|
|**References**|||
|**Personal Pro**|**file**||



ii 

### **List of Figures** 

|||Page No.|
|---|---|---|
|Figure 5.1|Architecture of the proposed system|24|
|Figure 5.2|System Flowchart|25|
|Figure 5.3|User-friendly registration page interface|26|
|Figure 5.4|Home Page|26|
|Figure 5.5|Weather Page|27|
|Figure 5.6|Market Page|27|
|Figure 5.7|Disease Detection Page|28|



iii 

### **List of Tables** 

|||Page No.|
|---|---|---|
|Table 2.1|<br>Comparative Analysis|11|
|Table 4.1|<br>Hardware requirements|16|
|Table 4.2|<br>Software requirements|16|
|Table 4.3|CNN Architecture|17|
|Table 4.4|Network Architecture|19|
|Table 4.5|Priority Matrix|20|
|Table 4.6|Agent weights|21|
|Table 7.1|Tasks Completed during current Semester|30|
|Table 7.2|Tasks to be completed during next Semester|30|



iv 

#### **Chapter 1** 

### **Introduction** 

#### **1.1 Project Introduction** 

Agriculture plays a crucial role in the economy of many countries, especially in rural regions where farming is the primary source of livelihood. Arecanut farming is widely practiced in several parts of India, particularly in Karnataka. However, farmers often face challenges in maintaining crop health due to delayed disease detection, unpredictable weather conditions, and fluctuating market prices. 

Traditional farming methods rely heavily on manual inspection and farmer experience to identify crop diseases or nutrient deficiencies. This approach is often inaccurate and timeconsuming, leading to late treatment and reduced crop productivity. Additionally, lack of real-time weather insights and market trend analysis prevents farmers from making informed decisions regarding irrigation, disease prevention, and selling strategies. 

Recent advancements in Artificial Intelligence (AI), Machine Learning (ML), and multiagent systems have created new opportunities for intelligent agricultural solutions. These technologies can analyze crop images, monitor environmental conditions, predict market prices, and provide timely recommendations to farmers. 

The proposed system, Areca Agent, is a Multi-Agent Intelligent Farming Ecosystem designed to assist arecanut farmers by integrating computer vision, weather intelligence, and market analysis. The system uses multiple intelligent agents such as Vision Agent,Monitoring Agent, Weather Agent, Market Analysis Agent, and Advisory Agent to collect and process agricultural data. These agents collaborate through a coordinator agent to  provide accurate recommendations and alerts to farmers. 

By enabling early disease detection, weather-based risk alerts, and market price forecasting, the system aims to improve crop health management, optimize farming practices, and increase farmer profitability. 

1 

#### **1.2 Problem Description** 

Arecanut is a highly valuable commercial crop, but its cultivation is highly susceptible to various pathological threats. Farmers face serious and continuous challenges in maintaining optimal crop health, primarily due to the late detection of severe leaf diseases and critical nutrient deficiencies. The inability to identify these threats in their nascent stages remains a fundamental bottleneck in achieving high agricultural productivity. 

Currently, farmers in rural and semi-urban agricultural belts rely overwhelmingly on manual, visual inspection or the limited availability of expert agricultural guidance. This traditional approach makes accurate problem identification exceptionally difficult. The complexity is further exacerbated when different plant diseases or nutritional deficiencies present with similar visual symptoms, making human error highly probable even among experienced cultivators. 

This reliance on outdated monitoring methods creates a cascading series of negative outcomes. Delayed or incorrect diagnoses frequently result in the application of improper treatments. Consequently, farmers often resort to the excessive and preemptive use of chemical pesticides and fertilizers. This not only significantly increases the operational costs of farming but also degrades soil health over time. Ultimately, these inefficiencies culminate in substantially reduced crop yields and a degradation in the overall quality of the harvested nuts, directly impacting the farmer’s livelihood. 

Furthermore, contemporary arecanut farming practices suffer from a severe technological deficit. There is exceedingly limited use of real-time data, environmental monitoring, or modern predictive technologies. Factors that heavily influence disease proliferation, such as humidity and rainfall, are rarely integrated into treatment planning. Additionally, farmers lack access to predictive market intelligence, leaving them vulnerable to price volatility and unable to optimize their harvesting and selling schedules for maximum profit. To comprehensively address these interconnected issues, there is a critical and urgent need for an advanced, AI-driven monitoring ecosystem. The arecanut agricultural sector requires a robust system capable of autonomous, early disease detection using computer vision, coupled with weather-based risk analysis and market forecasting. By bridging this technological gap, farmers can be provided with accurate, real-time guidance and actionable advisories, thereby facilitating better decision-making to fundamentally improve the productivity, profitability, and long-term sustainability of arecanut farming. 

2 

**Chapter 2** 

### **Literature Review** 

#### **2.1 Literature Survey** 

In the paper titled _“A Literature Review of the Detection and Categorization of various Arecanut Diseases using Image Processing and Machine Learning Approaches”_ [1], the authors Puneeth B. R. and Nethravathi P. S. present a survey on techniques for detecting and classifying arecanut diseases. The paper highlights that arecanut is a major commercial crop in India but is highly affected by diseases such as Koleroga, bud rot, and yellow leaf disease, causing significant yield loss. Traditional detection methods are manual and inefficient, creating the need for automated solutions. The authors review various image processing and machine learning techniques including CNN, KNN, SVM, and Decision Trees. Key steps such as image preprocessing, segmentation, feature extraction, and classification are discussed. The study observes that most research focuses on grading rather than early disease detection. It identifies a major research gap in developing efficient early detection systems and concludes that combining machine learning with image processing can improve accuracy and support farmers in reducing crop loss. 

In the paper titled _“CNN Based Method for Multi-Type Diseased Arecanut Image Classification”_ [2], the authors S. B. Mallikarjuna et al. propose a deep learning approach for classifying arecanut images affected by diseases such as rot, split, and rot-split. These diseases significantly reduce crop quality and yield, making manual classification inefficient and costly. To address this, the authors combine multi-gradient image processing with Convolutional Neural Networks (CNN). Multi-Sobel filters are applied to enhance edge details and reduce distortion in diseased images, which are then fed into a modified AlexNet model for classification into four classes: healthy, rot, split, and rot-split. The dataset is created and expanded using augmentation techniques like rotation, flipping, and blurring to improve performance. The proposed CNN model effectively extracts features using convolutional and pooling layers. Experimental results show that the method outperforms traditional approaches such as KNN and texture-based methods. The study concludes that this approach enables accurate multi-class classification of arecanut diseases. 

3 

In the paper titled _“ArecaShield: AI Powered Arecanut Disease Detection and Advisory System”_ [3], the authors Pallavi Shetty et al. present an AI-based integrated system designed to assist arecanut farmers in disease detection and decision-making. The study highlights that arecanut crops are highly affected by diseases such as Yellow Leaf Disease, Mahali Koleroga, and Stem Bleeding, which reduce yield and require timely intervention. To address this, the authors propose ArecaShield, which combines deep learning, weather forecasting, and a rule-based chatbot into a single platform. A ResNet20v1 CNN model is used for classifying images into nine disease and healthy categories, achieving an accuracy of about 96% . The system also integrates weather APIs to provide real-time forecasts and advisory suggestions, while a chatbot answers farmer queries efficiently. The platform is designed to be user-friendly and accessible in low-bandwidth rural areas. The study concludes that ArecaShield improves disease management, supports precision agriculture, and helps farmers reduce crop loss and improve productivity. 

In the paper titled _“Artificial Intelligence in Agriculture”_ [4], the author Deepesh Sharma discusses the growing role of artificial intelligence in transforming modern agriculture. The paper highlights that traditional farming methods are no longer sufficient to meet increasing food demands, and AI-based solutions are essential for improving productivity and efficiency. Various applications of AI are explored, including weather and price forecasting, crop health monitoring, agricultural robotics, intelligent spraying, and disease diagnosis . AI-based image recognition helps in detecting plant diseases, pests, and nutrient deficiencies, enabling timely intervention. The concept of precision farming is also emphasized, where AI ensures optimal use of resources such as water, fertilizers, and pesticides. The paper further discusses advantages such as better decision-making, cost savings, and reduction in labor dependency. However, challenges like lack of awareness, limited technical knowledge, and security issues are also identified. The study concludes that AI has strong potential to revolutionize agriculture, though wider adoption is necessary for maximum benefits. 

In the paper titled _“Crop Price Prediction using Supervised Machine Learning Algorithms”_ [5], the authors Ranjani Dhanapal et al. focus on predicting crop prices to help farmers make informed decisions and reduce financial losses. The study highlights that price fluctuations in agricultural markets significantly affect farmers’ income and overall economic stability. To address this issue, the authors propose a prediction model using a Decision Tree Regressor, a supervised machine learning algorithm, trained on 

4 

historical rainfall data and Wholesale Price Index (WPI) . The methodology includes data collection from government sources, data cleaning, exploratory data analysis, and model training. The system predicts crop prices for the next 12 months and presents the results through a user-friendly web application. Experimental results show that the decision tree model provides accurate predictions with low error compared to other algorithms. The study concludes that such predictive systems can help farmers plan crop selection, reduce risks, and improve profitability through better decision-making. 

In the paper titled _“Machine Learning and IoT-Based Smart Farming for Enhancing the Crop Yield”_ [6], the authors propose an integrated smart agriculture system that combines machine learning and IoT technologies to improve crop productivity. The system focuses on three major components: crop recommendation, automatic irrigation, and fertilizer suggestion. It analyzes key parameters such as soil nutrients (N, P, K), pH values, temperature, humidity, and rainfall to recommend suitable crops. The methodology uses multiple machine learning models including KNN, Decision Tree, Random Forest, Gradient Boosting, and XGBoost, where KNN achieved the best performance with high accuracy. Additionally, the system incorporates IoT sensors for real-time monitoring of soil moisture and environmental conditions, enabling automated irrigation decisions. It also provides fertilizer recommendations based on soil fertility analysis. The proposed system reduces manual effort, optimizes resource usage, and enhances crop yield, making it a practical decision-support tool for farmers. 

In the paper titled _“Phytophthora Diseases of Arecanut in India: Prior Findings, Present Status and Future Prospects”_ [7], the authors Patil Balanagouda et al. present a comprehensive review of major diseases affecting arecanut caused by _Phytophthora_ species. The study highlights that diseases such as fruit rot, bud rot, and crown rot are highly destructive, causing yield losses ranging from 10% to 100% under severe conditions. These diseases are widely prevalent in high rainfall regions of India, especially during the southwest monsoon season. The pathogen _Phytophthora meadii_ is identified as the primary causal agent, and its spread is influenced by environmental factors such as humidity, rainfall, and temperature . The paper discusses symptoms, epidemiology, and pathogen survival mechanisms, including its persistence in soil and infected plant material. Various management strategies such as chemical control (Bordeaux mixture), biological agents, plant extracts, and cultural practices are reviewed. The study concludes that lack of resistant varieties and difficulty in field management 

5 

remain major challenges, emphasizing the need for advanced disease prediction and sustainable control methods. 

In the paper titled _“Predictive Analytics in Agriculture: Forecasting Prices of Arecanuts in Kerala”_ [8], the authors Kiran M. Sabu and T. K. Manoj Kumar focus on predicting arecanut prices using time-series and machine learning techniques. The study highlights that price fluctuations significantly impact farmers’ income and decision-making, often leading to financial instability. To address this, the authors use historical price data from 2007 to 2017 collected across 14 districts of Kerala. The methodology involves applying models such as SARIMA, Holt-Winter’s Seasonal method, and LSTM neural networks to capture trends and seasonality in the data. The report captures a clear upward trend and seasonal variation in arecanut prices, confirming the need for advanced forecasting models. Experimental results indicate that the LSTM model outperforms traditional statistical models with the lowest RMSE value, providing more accurate predictions . The study concludes that predictive analytics can help farmers and stakeholders make informed decisions, reduce risks, and improve economic outcomes in agriculture. 

In the paper titled _“Machine Learning in Agriculture: A Review”_ [9], the authors Konstantinos G. Liakos et al. present a comprehensive overview of machine learning applications in modern agriculture. The study categorizes applications into four major domains: crop management, livestock management, water management, and soil management. It highlights how machine learning models such as Artificial Neural Networks (ANNs), Support Vector Machines (SVMs), and Decision Trees are widely used for tasks like yield prediction, disease detection, and soil analysis. A typical machine learning workflow involves training models using historical data and applying them to predict or classify new data, emphasizing its importance in agriculture . The study concludes that integrating sensor data with machine learning enables real-time decision-making systems, improving productivity, sustainability, and precision farming practices. 

In the paper titled _“Soil Fertility Status as Influenced by Arecanut Based Cropping System and Nutrient Management”_ [10], Ravi Bhat and S. Sujatha investigate how integrated nutrient management affects soil fertility and crop productivity in arecanut-based systems. The study, conducted at Central Plantation Crops Research Institute, analyzed different treatments combining organic matter recycling (OMR) with chemical fertilizers. Results show that recyclable biomass ranged from 8.72 to 10.35 

6 

t/ha/year and significantly contributed to soil nutrient enrichment. It indicates that arecanut equivalent yield increased from 1777 kg/ha in 1999 to 2769 kg/ha in 2002, demonstrating improved productivity . The study also highlights that OMR maintains adequate nitrogen and phosphorus levels, while potassium requires additional supplementation due to heavy crop demand. Overall, the findings suggest that integrating organic recycling with fertilizers enhances sustainability, improves soil health, and supports long-term agricultural productivity. 

In the paper titled _“Effect of Organic and Inorganic Sources of Nutrients on Soil Fertility Status of Arecanut (Areca catechu) in North-East India”_ [11], the authors G. C. Acharya et al. study the impact of different nutrient sources on soil properties and arecanut yield. The research compares vermicompost, common compost, chemical fertilizers, and control conditions in an arecanut plantation. The findings show that soils treated with vermicompost had the highest nitrogen content and improved organic carbon, water holding capacity, and microbial activity. It indicates that vermicompost increased available nitrogen to 332.6 kg/ha, while chemical fertilizers resulted in higher phosphorus and potassium levels . The study also highlights that organic treatments significantly increased earthworm and microbial populations, improving soil health. Yield results demonstrate that vermicompost produced the highest dry yield (4496.9 kg/ha), outperforming chemical fertilizers and control plots. The study concludes that integrated nutrient management, especially organic sources, enhances soil fertility, sustainability, and crop productivity in arecanut farming. 

In the paper titled _“Influence of Weather Parameters on Yield and Yield Attributes of Areca Nut (Areca catechu L.)”_ [12], the authors K. M. Sunil et al. analyze the impact of climatic factors on arecanut yield. The study highlights that weather parameters such as temperature, rainfall, and relative humidity play a crucial role in determining crop productivity. Based on long-term data collected from 1991 to 2006, the results show that minimum temperature, relative humidity, and moderate rainfall during the flowering stage (January–March) positively influence yield. However, excessive rainfall during the nut development stage negatively affects productivity by disrupting pollination and increasing disease incidence. The result shows variations in yield across years, with the highest yield recorded at 25,409 kg/ha under favorable weather conditions . The study also develops regression models to predict yield based on rainfall and temperature. It concludes that understanding weather patterns is essential for improving yield prediction and effective crop management in arecanut cultivation. 

7 

In the paper titled _“Characterisation and Classification of Arecanut-Growing Soils of Karnataka, India”_ [13], the authors R. Vasundhara et al. analyze the physical, chemical, and morphological properties of soils supporting arecanut cultivation across different agro-climatic zones of Karnataka. The study highlights that arecanut-growing soils vary significantly depending on climatic conditions, ranging from acidic soils in coastal and hilly regions to neutral or alkaline soils in dry zones. The soils are generally deep, well-drained, and have textures ranging from sandy clay loam to clay, supporting good water retention. It shows that cation exchange capacity (CEC) ranges from 2.5 to 32.6 cmol/kg, indicating variability in nutrient-holding capacity . The study also finds that organic carbon content is higher at the surface and decreases with depth, influencing soil fertility. Based on soil taxonomy, the soils are classified into Alfisols, Inceptisols, and Ultisols. The study concludes that understanding soil characteristics is essential for improving crop management, nutrient application, and sustainable arecanut production. 

In the paper titled _“Diseases of Arecanut and their Management”_ [14], the authors Vinod Upadhyay and Elangbam Premabati Devi provide a detailed overview of major diseases affecting arecanut and their management strategies. The study highlights that arecanut cultivation faces significant yield losses due to diseases such as fruit rot (Koleroga), basal stem rot, yellow leaf disease, leaf spot, and bacterial leaf stripe. It lists key diseases along with their causal organisms, including _Phytophthora meadii_ , _Ganoderma lucidum_ , and _Xanthomonas campestris_ . The paper explains symptoms, epidemiology, and favorable environmental conditions for disease spread, such as high humidity and monsoon rainfall. It also discusses integrated disease management practices including cultural methods, chemical treatments like Bordeaux mixture and fungicides, and phytosanitary measures. The study emphasizes that early detection and proper management are crucial to reduce crop loss. It concludes that developing disease-resistant varieties and adopting advanced technologies like GIS and molecular techniques are essential for sustainable arecanut cultivation. 

In the paper titled _“Forecasting Areca Nut Market Prices Using the ARIMA Model: A Case Study of India”_ [15], the authors Abhaya K. Kumar et al. propose a time-series forecasting approach to predict arecanut prices in Karnataka. The study highlights that price volatility is a major challenge for farmers and traders due to fluctuating demand, labor issues, and international trade dynamics. The authors use monthly price data from 2009 to 2018 and apply the Box-Jenkins ARIMA methodology for modeling. It shows an upward trend in arecanut prices, indicating non-stationarity, which is corrected using 

8 

first-order differencing . Further, ACF and PACF correlograms are used to identify suitable model parameters. Among multiple tested models, ARIMA (3,1,3) is selected as the best model based on statistical measures such as AIC, BIC, and log-likelihood. The study concludes that accurate price forecasting models can help farmers and policymakers make informed decisions, reduce financial risk, and improve market stability. 

In the paper titled _“Prediction of Fruit Rot Disease Incidence in Arecanut Based on Weather Parameters”_ [16], the authors K. Rajashree et al. propose a deep learning-based approach to forecast fruit rot disease (FRD) in arecanut crops. The study emphasizes that FRD is highly influenced by environmental factors such as rainfall, humidity, and temperature, causing up to 70% yield loss in severe cases . The authors use 21 years of weather data (2000–2020) from Udupi along with disease incidence data to build prediction models. As shown in the _flow diagram on page 5_ , the methodology involves data collection, preprocessing, and application of deep learning models like Vanilla LSTM, Stacked LSTM, Bidirectional LSTM, and GRU. The dataset is processed to generate a disease score value based on specific weather conditions. Among all models, the Vanilla GRU model performs best with the lowest Mean Square Error (1.3), outperforming other LSTM variants. The study concludes that integrating weather data with deep learning models enables early disease prediction, helping farmers take preventive measures and reduce crop losses. 

In the paper titled _“Identification and Categorization of Diseases in Arecanut: A Machine Learning Approach”_ [17], the authors Ajit Hegde et al. propose a CNN-based system for detecting and classifying arecanut diseases. The study highlights that traditional visual inspection methods are time-consuming and require expert knowledge, making automated solutions necessary. The proposed system uses a proprietary dataset of over 1,100 images of healthy and diseased arecanut, including leaves, nuts, and trunks, collected from Karnataka regions . The methodology involves preprocessing steps such as resizing images to 256×256, normalization, and data augmentation, followed by training a Convolutional Neural Network model. the CNN consists of convolutional, pooling, dropout, and fully connected layers for feature extraction and classification. The system classifies diseases such as fruit rot, stem bleeding, yellow leaf spot, and nut split, achieving an accuracy of 93.05%. The study concludes that CNN-based approaches provide efficient and accurate disease detection, helping farmers take timely preventive actions. 

9 

In the paper titled _“Efficient Deep Learning Framework for Arecanut Disease Detection Using Graph Neural Network and Bat Algorithm”_ [18], the authors Finney Daniel Shadrach et al. propose an advanced hybrid deep learning model combining Graph Neural Networks (GNN) and the Bat Algorithm (BA) for accurate disease detection in arecanut crops. The study highlights challenges in traditional CNN-based approaches, such as limited ability to capture complex spatial relationships and poor performance under real-field conditions. To address this, the proposed system models leaf images as graphs to capture non-Euclidean spatial features, while the Bat Algorithm optimizes hyperparameters for improved performance. The dataset consists of a curated subset of 1,000 images from a larger Kaggle dataset, covering nine disease categories. The system includes preprocessing, graph construction, GNN-based feature extraction, and classification. Experimental results show that the model achieves 98.45% accuracy, outperforming traditional models like CNN-ViT and CBAM. The study concludes that the hybrid GNN-BA approach provides efficient, accurate, and scalable disease detection for precision agriculture. 

In the paper titled _“Disease Diagnosis and Sustainable Prevention in Arecanut Farming”_ [19], the authors Sneha Chikkanayakanahalli Siddalingadevaru et al. propose a deep learning-based approach for early detection and prevention of arecanut diseases. The study highlights that arecanut crops are highly affected by diseases such as Yellow Leaf Spot, Koleroga, Stem Bleeding, and Bud Borer, leading to significant yield loss. Traditional manual inspection methods are time-consuming and inefficient for large-scale monitoring. To overcome this, the authors use Convolutional Neural Networks (CNN) with an Extension model for accurate disease classification. The dataset consists of around 8844 images collected from Kaggle along with additional real-world images captured from farms. The system includes preprocessing, convolutional layers, pooling, and fully connected layers for classification. Experimental results demonstrate that the proposed model achieves an accuracy of 98.9%, outperforming traditional methods like SVM and basic CNN models. The study concludes that the system enables real-time disease detection and provides preventive measures, helping farmers improve crop productivity. 

10 

In the paper titled _“Detection of Diseases in Arecanut Using Convolutional Neural Networks”_ [20], the authors Anilkumar M G et al. propose a machine learning-based system for detecting diseases in arecanut plants using image processing techniques. The study highlights that traditional disease detection through manual observation is time-consuming, labor-intensive, and ineffective for early diagnosis. To address this, the authors use Convolutional Neural Networks (CNN) to classify diseases such as Mahali (Koleroga), Stem Bleeding, and Yellow Leaf Spot. The dataset consists of 620 images of healthy and diseased arecanut leaves, nuts, and trunks, divided into an 80:20 training and testing ratio . The system involves preprocessing steps such as image resizing, normalization, and augmentation, followed by feature extraction and classification using CNN layers. The process includes preprocessing, training, and prediction stages. Experimental results demonstrate that the model achieves an accuracy of 88.46%. The study concludes that the proposed system provides an effective automated solution for disease detection and supports smart farming practices. 

#### **2.2 Comparative Analysis of the Related Work** 

The table 2.1 discusses the comparative analysis of the current systems in light of the suggested proposal. 

**Table 2.1: Comparative Analysis** 

|**Sl.**<br>**No**|**Author(s)**|**Algorithms/Techniques**|**Performance**<br>**Measures**|
|---|---|---|---|
|1|Puneeth B. R.,<br>Nethravathi P. S.|CNN, KNN, SVM, Decision Tree,<br>Image Processing|Accuracy|
|2|S. B. Mallikarjuna et al.|CNN (Modified AlexNet),<br>Multi-Sobel Filters|Accuracy,<br>Precision,<br>Recall|
|3|Pallavi Shetty et al.|CNN (ResNet20v1), Weather API,<br>Chatbot|Accuracy<br>(~96%)|
|4|Deepesh Sharma|Artificial Intelligence, Image<br>Recognition, Robotics|Efficiency,<br>Accuracy|
|5|Ranjani Dhanapal et al.|Decision Tree Regressor|Accuracy,<br>Error Rate|



11 

|6|(Smart Farming Paper<br>Authors)|KNN, Decision Tree, Random<br>Forest, Gradient Boosting, XGBoost,<br>IoT|Accuracy|
|---|---|---|---|
|7|Patil Balanagouda et al.|Disease Analysis, Biological &<br>Chemical Methods|Yield Loss %,<br>Effectiveness|
|8|Kiran M. Sabu, T. K.<br>Manoj Kumar|SARIMA, Holt-Winter, LSTM|RMSE,<br>Accuracy|
|9|Konstantinos G. Liakos<br>et al.|ANN, SVM, Decision Tree, ML<br>Models|Accuracy|
|10|Ravi Bhat, S. Sujatha|Organic Recycling + Fertilizer<br>Techniques|Yield, Soil<br>Fertility|
|11|G. C. Acharya et al.|Vermicompost, Chemical Fertilizers|Yield,<br>Nutrient<br>Content|
|12|K. M. Sunil et al.|Regression Models, Weather<br>Analysis|Yield<br>Prediction<br>Accuracy|
|13|R. Vasundhara et al.|Soil Classification, Chemical<br>Analysis|Soil Quality<br>Metrics|
|14|Vinod Upadhyay,<br>Elangbam Premabati<br>Devi|Disease Identification, Chemical<br>Control Methods|Effectiveness|
|15|Abhaya K. Kumar et al.|ARIMA Time Series Model|RMSE, AIC,<br>BIC|
|16|K. Rajashree et al.|LSTM, GRU, Deep Learning Models|MSE (Error<br>Rate)|
|17|Ajit Hegde et al.|CNN, Image Processing|Accuracy<br>(93.05%)|
|18|Finney Daniel Shadrach<br>et al.|Graph Neural Network (GNN), Bat<br>Algorithm|Accuracy<br>(98.45%)|
|19|Sneha<br>Siddalingadevaru et al.|CNN with Extension Model|Accuracy<br>(98.9%)|
|20|Anilkumar M G et al.|CNN, Image Processing|Accuracy<br>(88.46%)|



12 

#### **2.3 Summary** 

The literature survey provides a comprehensive understanding of various techniques used in arecanut disease detection, crop management, and smart agriculture systems. From the reviewed papers, it is evident that traditional methods of disease identification based on manual observation are time-consuming, less accurate, and not suitable for large-scale farming. With the advancement of technology, machine learning and deep learning techniques such as Convolutional Neural Networks (CNN), Support Vector Machines (SVM), K-Nearest Neighbors (KNN), and Random Forest have been widely adopted for accurate and automated disease detection. Among these, CNN-based models have shown superior performance due to their ability to extract complex features from images and achieve high accuracy. 

In addition, several studies highlight the importance of integrating technologies such as IoT, weather forecasting models, and predictive analytics for improving crop yield and decision-making. Techniques like LSTM, ARIMA, and regression models are effectively used for price prediction and disease forecasting. Soil analysis and nutrient management studies also emphasize the role of sustainable farming practices in enhancing productivity. 

Overall, the survey indicates that combining deep learning, IoT, and data-driven approaches can significantly improve disease detection, reduce crop loss, and support precision agriculture. These insights form the foundation for developing an efficient and intelligent Areca Agent system 

13 

**Chapter 3** 

### **Problem Formulation** 

#### **3.1 Problem Statement** 

Arecanut farmers face serious challenges in maintaining crop health due to late detection of diseases and nutrient deficiencies. Farmers in rural areas rely heavily on manual inspection or limited expert guidance, making accurate problem identification difficult, especially when different diseases present similar symptoms. This delayed or incorrect diagnosis directly results in improper treatment, excessive pesticide use, increased operational costs, reduced yield, and poor nut quality. Furthermore, there is limited use of real-time data and modern technology in current arecanut farming practices, leaving crops vulnerable.Therefore, an AI-driven system is urgently required for arecanut crops to enable early disease detection, provide accurate guidance, and facilitate better decision-making to improve productivity and sustainability. 

#### **3.2 Objectives of the Present Study** 

The primary objectives of the proposed system are as follows: 

1. To design and develop a Multi-Agent Agentic AI system for intelligent arecanut crop monitoring and decision support. 

2. To enable early disease detection of arecanut leaf diseases using computer vision techniques. 

3. To integrate weather-based risk alerts using real-time API data. 

4. To forecast market price trends and autonomously notify farmers for economically optimal decision-making. 

#### **3.3 Summary** 

The problem formulation of this project centers on the critical inefficiencies and risks inherent in traditional arecanut farming practices. Specifically, the reliance on manual inspection leads to late detection of crop diseases, resulting in the overuse of pesticides, 

degraded nut quality, and significant economic losses. This vulnerability is compounded by the lack of real-time environmental and market data utilization. To address these issues, this study aims to develop ‘ArecaAgent’, a comprehensive, AI-driven Multi-Agent System. The system’s core objectives are to automate early disease detection using computer vision, forecast weather-related crop risks, predict market price trends, and deliver actionable, autonomous advisories to farmers. By bridging the gap between 

14 

modern artificial intelligence and grassroots agriculture, this research strives to resolve the identified problems and enhance the productivity, profitability, and sustainability of arecanut cultivation. 

15 

**Chapter 4** 

### **Requirements and Methodology** 

#### **4.1 Hardware Requirements** 

The hardware requirements for the proposed project are depicted in Table 4.1. 

**Table 4.1: Hardware requirements** 

|**Sl. No**|**Hardware/Equipment**|**Specification**|
|---|---|---|
|1.|Graphics Card|Intel 621 Graphics card or 2GB|
|2.|RAM|4GB or above|
|3.|Development Board|Robozar ESP32|
|4.|Soil Moisture Sensor|Capacitive Soil Moisture Sensor Module|
|5.|Local Output Display|0.96 Inch OLED Display|



#### **4.2 Software Requirements** 

The software requirements for the proposed project are depicted in Table 4.2. 

**Table 4.2: Software requirements** 

|**Sl. No**|**Software**|**Specification**|
|---|---|---|
|1.|Anaconda|Anaconda 64 bit|
|2.|Python|Python 3.14 or above|
|3.|Framework|FastAPI|



#### **4.3 Datasets Required** 

##### **4.3.1.Dataset for Arecanut disease Detection** 

1.Arecanut Classification Dataset from Kaggle <u>https://www.kaggle.com/datasets/tejpaviraj/arecanut</u> 

2.Local dataset from Rural farms 

##### **4.3.2.Dataset for Market Price Prediction and Validation** 

1.The live API From data.gov.in under the name “Variety-wise Daily Market Prices Data of Commodity” and “arecanut” as commodity 

16 

#### **4.4 Algorithms Required** 

##### **4.4.1. Vision Agent - Convolutional Neural Network (CNN) for Disease** 

##### **Detection** 

Purpose: Analyze leaf images to detect and classify arecanut diseases using deep learning. 

**Table 4.3 : CNN Architecture** 

|**Layer Type**|**Configuration**|**Purpose**|
|---|---|---|
|Input|RGB leaf images<br>(224×224 pixels)|Image preprocessing and<br>normalization|
|Conv Layers|4 blocks (3×3 filters,<br>ReLU, MaxPool)|Extract hierarchical features from<br>images|
|Fully Connected|256 units, Dropout<br>(0.5), Softmax|Classification probability distribution|
|Output|Disease class and<br>confidence score (%)|Disease identification with confidence|



Key Features 

- Transfer Learning: Uses pre-trained weights from PlantVillage dataset 

- Data Augmentation: Rotation, zoom, brightness adjustment for robust detection 

- Real-time Inference: Optimized for mobile and edge devices 

- Confidence Thresholding: Only reports detections above 70% confidence 

##### **4.4.2. Diagnosis Agent - Bayesian Inference for Disease Validation** 

Purpose: Validate CNN predictions using environmental conditions and historical data to reduce false positives. 

###### **Algorithm: Bayes' Theorem** 

_P(Disease | Image, Weather, History) = P(Image | Disease) × P(Weather | Disease) × P(Disease) / P(Evidence)_ 

Where: 

- P(Image | Disease): CNN confidence from Vision Agent 

- P(Weather | Disease): Environmental favorability (temperature, humidity, rainfall) 

- P(Disease): Historical occurrence frequency in the region 

17 



<!-- Start of picture text -->
yt=ut LXoi(v't-i) + LOU (et-j) + et<br>* 0): Moving Average parameters<br><!-- End of picture text -->

##### **4.4.4. Market Analysis Agent - LSTM for Price Forecasting** 

Purpose: Predict arecanut market prices using historical data and external factors. 

###### **Algorithm: Long Short-Term Memory (LSTM) Neural Network** 

_LSTM processes temporal sequences to learn complex price patterns from 60-day historical data_ 

**Table 4.4 : Network Architecture** 

|**Layer**|**Config**|**Purpose**|
|---|---|---|
|Input|60-day price history, volume,<br>seasonal factors|Temporal sequence input|
|LSTM 1|128 units, 20% dropout, ReLU|Learn long-term dependencies|
|LSTM 2|64 units, 20% dropout|Refine temporal patterns|
|Output|7-day ahead price prediction|Price forecast for decision-making|



###### **Training Details** 

- Loss Function: Mean Absolute Percentage Error (MAPE) 

- Optimizer: Adam with learning rate 0.001 

- Training Data: 5 years of daily market prices 

- Retraining: Weekly with new data to adapt to market trends 

##### **4.4.5. Advisory Agent - Rule-Based Expert System** 

Purpose: Generate actionable farming recommendations by combining outputs from all agents. 

###### **Decision Rules (IF-THEN Logic)** 

- IF disease_confidence > 85% AND weather_favorable THEN recommend fungicide treatment 

- IF humidity > 85% AND temperature 22-28°C THEN alert high disease risk 

- IF predicted_rainfall > 10mm AND disease_detected THEN recommend pesticide application before rain 

- IF market_price_trend increasing AND crop_health > 80% THEN recommend delay harvest 

19 

•   IF nutrient_deficiency detected THEN recommend fertilizer schedule and type 

**Table 4.5 : Priority Matrix** 

|**Priority**|**Condition**|**Action**|
|---|---|---|
|URGENT|Critical disease + high humidity +<br>rainfall imminent|Immediate SMS + app<br>notification|
|HIGH|Disease detected + unfavorable weather|Alert + advisory within 2<br>hours|
|MEDIUM|Moderate risk or market opportunity|In-app notification within<br>24 hours|
|LOW|General information or trend|Dashboard update only|



##### **4.4.6. Learning Agent - Reinforcement Learning for System Optimization** 

Purpose: Continuously improve system recommendations based on farmer feedback and real outcomes. 

###### **Algorithm: Q-Learning** 

_Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]_ 

Where: 

- s: Current state (farm conditions + crop health) 

- a: Action (advisory recommendation) 

- r: Reward (outcome score from farmer feedback) 

- α: Learning rate (0.1) 

- γ: Discount factor (0.9) 

###### **Feedback Loop** 

- Farmer rates recommendation effectiveness (1-5 stars) 

- System captures outcome metrics (crop yield, disease reduction, profit) 

- Q-values updated to reflect successful vs. unsuccessful actions 

- Model retraining scheduled monthly with accumulated feedback 

20 

##### **4.4.7. Coordinator Agent - Multi-Agent Orchestration** 

Purpose: Integrate outputs from all specialized agents and resolve conflicts through weighted consensus. 

**Table 4.6 : Agent Weights** 

|**Agent**|**Weight**|**Justification**|
|---|---|---|
|Diagnosis Agent|35%|Disease detection critical|
|Weather Agent|30%|Risk amplification factor|
|Market Agent|20%|Economic optimization|
|Learning Agent|15%|Continuous improvement|



#### **4.5 Methodology** 

##### **4.5.1 Overview of the Proposed Methodology** 

The proposed system, ArecaAgent, employs a Multi-Agent System (MAS) architecture to deliver an intelligent crop health monitoring and decision-support platform for arecanut farming. The methodology integrates computer vision, probabilistic reasoning, time-series forecasting, rule-based logic, and reinforcement learning across specialized, collaborating AI agents. This decentralized approach allows for modular data processing and robust decision-making. 

##### **4.5.2 Data Acquisition and Preprocessing** 

The system relies on diverse datasets for comprehensive analysis: 

1. Image Data: An Arecanut Classification Dataset from Kaggle combined with local datasets collected from rural farms for training computer vision models. 

2. Market Data: Live API integration from data.gov.in fetching ‘Variety-wise Daily Market Prices Data of Commodity’ for arecanut. 

3. Environmental Data: Weather data sourced via external APIs (OpenWeatherMap,NOAA) and local IoT sensors capturing temperature, humidity, and soil moisture. 

##### **4.5.3 Multi-Agent Architecture and Algorithms** 

The core of the methodology revolves around a suite of specialized agents, each employing specific algorithms to perform dedicated tasks: 

21 

###### **4.5.3.1 Vision Agent (Disease Detection)** 

Algorithm: Convolutional Neural Network (CNN). 

The Vision Agent analyzes RGB leaf images (224x224 pixels) to detect and classify diseases. It utilizes transfer learning (pre-trained weights from the PlantVillage dataset) and data augmentation techniques. The architecture consists of 4 convolutional blocks followed by fully connected layers, outputting a disease class and a confidence score. Detections are reported if the confidence exceeds 70%. 

###### **4.5.3.2 Diagnosis Agent (Validation)** 

Algorithm: Bayesian Inference. 

To reduce false positives, the Diagnosis Agent validates the CNN’s predictions using Bayes’Theorem. It computes the posterior probability of a disease by combining the image confidence score with environmental favorability (weather data) and historical disease occurrence frequencies. A validated diagnosis is generated if the posterior probability exceeds 75%. 

###### **4.5.3.3 Weather Agent (Risk Forecasting)** 

Algorithm: AutoRegressive Integrated Moving Average (ARIMA). 

This agent monitors 6-hourly real-time environmental conditions and performs time-series forecasting. It calculates a weighted &#39;Disease Risk Score’s based on factors like high humidity, temperature ranges, and imminent rainfall. 

###### **4.5.3.4 Market Analysis Agent (Price Prediction)** 

Algorithm: Long Short-Term Memory (LSTM) Neural Network. 

Using a 60-day historical window of market prices and volumes, the LSTM network processes temporal sequences to forecast 7-day ahead price trends. The model is optimized using the Adam optimizer and Mean Absolute Percentage Error (MAPE) loss function. 

###### **4.5.3.5 Advisory Agent (Expert System)** 

Algorithm: Rule-Based Expert System. 

This agent aggregates outputs from the predictive models and applies IF-THEN logic to generate actionable farming recommendations. Actions are categorized into Urgent, High, Medium, and Low priorities based on disease criticality and weather conditions. 

22 

###### **4.5.3.6 Learning Agent (System Optimization)** 

Algorithm: Q-Learning (Reinforcement Learning). 

The system continuously improves by capturing farmer feedback (ratings and outcome metrics like yield or disease reduction). Q-values are updated monthly to refine future recommendations, favoring highly rated advisory actions. 

###### **4.5.3.7 Coordinator Agent (Orchestration)** 

The Coordinator Agent integrates the outputs from all specialized agents. It resolves conflicts through a weighted consensus mechanism: Diagnosis Agent (35%), Weather Agent (30%), Market Agent (20%), and Learning Agent (15%). 

##### **4.5.4 Hardware and Software Implementation** 

The physical implementation integrates a Robozar ESP32 development board with a Capacitive Soil Moisture Sensor Module and a 0.96-inch OLED display. The software backbone is developed in Python 3.14+ utilizing the FastAPI framework within an Anaconda 64-bit environment. 

23 



<!-- Start of picture text -->
Mobile App Web Dashboard Farmer Alerts<br>———————— ——————Application &Ee API Layer ———————<br>REST API [ Request Router Notification Service [ Authentication own |<br>Multi-Agent Intelligence Layer (Core Al System)<br>Vision Diagnosis Weather Market Advisory Learning Notifying Monitoring<br>Agent Agent Agent Agent Agent Agent Agent Agent<br>© OE>mS italk &"5 la<br>Disease Validation Weather Price Treatment Feedback Alert System<br>Detection Check Analysis Predictions Advice & Update Delivery Monitoring<br>Coordinator Agent<br>Decision Integration<br>Data & Storage Layer<br>Crop Health DB Env. Data DB Market Data DB User Database System Logs DB<br>External Services Integration<br>“— eer &<br>Weather API Market Data Feeds SMS / Cloud Notifications Cloud Platform Cloud Infrastructure<br>(AWS / Azure / GCP) (AWS / Azure / GCP)<br><!-- End of picture text -->



<!-- Start of picture text -->
XS START<br>User Opens ArecaAgent App<br>and Logs In<br>User authenticates via mobile app<br>or web dashboard.<br>Select Service / Topic<br>User selects an option like Disease Detection,<br>Weather, Market Prices, or Advisory.<br><} Request Sent to System<br>f+) User request is routed through API Layer<br>| to the Core Al System. )<br>Multi-Agent Intelligence Layer Processes<br>gO «“SS a EF @ aa ul<br>Vision Diagnosis Weather Market Advisory Learning Notifying Monitoring<br>Agent Agent Agent Agent Agent Agent Agent Agent<br>‘Coordinator Agent integrates all agent outputs and generates final decision.<br><a> Data Retrieved & Stored<br>4 System retrieves required data and stores results in<br>‘Crop, Environmental, Market, User, and Logs Databases.<br>Recommendation & Alerts Generated<br>Personalized recommendations, predictions, and alerts<br>are prepared for the user.<br>« ) Results & Notifications Delivered<br>ry Recommendations, insights, and alerts are sent to the<br>user via app, dashboard, SMS, or push notifications. |<br>vt Progress Saved & System Monitored<br>pall User activity is saved, system performance is monitored,<br>and models are continuously improved.<br>> < END<br><!-- End of picture text -->



<!-- Start of picture text -->
ArecaAgent<br>Al-powered support for arecanut farmers in Karnataka<br>Username<br>farmer1<br>Phone<br>9876543210<br>Password<br><!-- End of picture text -->



<!-- Start of picture text -->
OAreca A sgent D ash boar:board _ DiiseaseDetectDetection Marar ke lt —Weathleather Advivisory SoilSoil MoniMoni t or facET) Ramesh GowdaVaesiend BL‘ogou it<br>Good morning,.  Ramesh Gowda<br>Saturday, 9 May 2026 Farm score refresh available<br>Farm Score 4 Today's Weather &a Market Price * Active Alerts a<br>29°C0; %420 9<br>78 72% humidity » Warm with Current Shimoga mandi price Unread notifications across<br>noo moderate humidity per kg the farm<br>4 12 from yesterday<br>Health, weather, and activity<br>readiness<br>(xHigh risk alert: Humidity remains elevated. Yellow Leaf Disease risk is high for the next 48 hours. 4|<br>7-DayaMarket Trend & Open market page Today'si  Reminders-<br>Predicted Shimoga market price trajectory<br>© Inspect leaf underside for early yellowing symptoms.<br>nn 2 * beer ip kntoetion before 3:90 AM.<br>©) Daview enray erhadiila aftar tha navt rainfall windew<br><!-- End of picture text -->



<!-- Start of picture text -->
© ArecaAgent Dashboard Disease-  Detection. Market Weather Advisory. _Soil.  Monitor. Pp Ramesh GowdaFARMER ? Logout<br>Weather Intelligence<br>Local rainfall, humidity, and spray timing insights<br>Temperature Humidity Rainfall Today Wind Speed<br>29°C°, 72%) 4mm 11 km/h<br>Yellow Leaf Disease Risk aan<br>Humidity above 70% with scattered showers makes leaf disease spread more likely.<br>SS)<br>HIGH risk<br>7-Day Forecast<br>Mon Tue Wed Thu Fri Sat Sun<br>or (Sy) GP (es) “O: (@) 1)<br>31° / 24° 30° / 23° 28° / 22° 29° / 22° 32°/ 24° 30° / 23° 27° / 22°<br>2mm rain 6 mm rain 14mm rain 8 mm rain Amm rain 5 mm rain 16 mm rain<br>© ArecaAgent Dashboard Disease.  Detection Market Weather Advisory _Soil Monitor P Ramesh GowdaFARMER © Logout<br>Market Prices.<br>Forecasts from the Market Agent for local mandi decisions<br>Current price SELECTED MANDI<br>ZA3ZA/kg = Mangalore v<br>\ %4 from yesterday Current prices are higher than the 7-day average, making it a good selling window.<br>7-DayActual vs Forecastpredicted prices ls 30-DayHistorical Trendmandi movement<br>}<br><!-- End of picture text -->



<!-- Start of picture text -->
73) ArecaAgent Dashboard Disease.  Detection Market Weather Advisory. Soil MonitorPs fad Ramech Gowda:FARMER © Logout<br>Disease Detection<br>Upload a leaf photo for Al analysis<br>H Drag & drop or click to upload |<br>| JPEG or PNG leaf photo |<br>- \ V4 P od & Vision Agent<br>’ .a. : ' f fy * Y; Yellow Leaf Disease 100% confidence _ high<br>WX . Z fjf - B a Model prediction from image analysis.<br>ot ‘ ‘ ; ?<br>b N ~~‘~ od\ 4 : Pe, pf ©DiagnosisDiagnosis confirmed Agent for Yellow Leaf Disease. Validation<br><!-- End of picture text -->

**Chapter 6** 

### **Conclusion** 

The proposed system, ArecaAgent, provides an efficient and intelligent solution for improving arecanut farming through the integration of Artificial Intelligence, Machine Learning, and Multi-Agent Systems. By combining disease detection, weather forecasting, market price prediction, and expert advisory mechanisms, the system helps farmers make accurate and timely decisions. 

The use of specialized agents enables faster data processing, early disease identification, and real-time monitoring of environmental conditions, thereby reducing crop damage, unnecessary pesticide usage, and operational costs. The system is designed to provide accurate recommendations with improved reliability through coordinated decision-making and continuous learning from farmer feedback. 

Additionally, the simple and user-friendly design allows even farmers with limited technical knowledge to easily access and use the application. When deployed on a larger scale, the system can significantly improve crop productivity, sustainability, and farmer profitability while promoting smarter and technology-driven agricultural practices. 

29 

**Chapter 7** 

### **Plan for Completion of Pending Work** 

The tasks accomplished during this semester are shown in Table 7.1. 

**Table 7.1: Tasks Completed during current Semester** 

|**Sl. No**|**Month**|**Task Completed**|
|---|---|---|
|1|February|Formulation of the project and identification of<br>problem statement|
|2|March|Literature survey and collection of datasets related<br>to arecanut farming|
|3|April|Design of Multi-Agent System architecture and<br>selection of algorithms|
|4|May|Initial implementation of Vision Agent, Weather|
|||Agent, and Market Analysis modules|



The tasks to be accomplished during next semester are shown in Table 7.2. 

**Table 7.2: Tasks to be completed during next Semester** 

|**Sl. No**|**Month**|**Task to be completed**|
|---|---|---|
|1|August|Development and integration of all intelligent<br>agents|
|2|September|Testing of disease detection and forecasting<br>models|
|3|October|Hardware integration using ESP32 and sensor<br>modules|
|4|November|System evaluation, performance analysis, and<br>optimization|
|5|December|Documentation, final report preparation, and<br>project presentation|



30 

### **References** 

[1] P. B. R. Puneeth and N. P. S. Nethravathi, “A Literature Review of the Detection and Categorization of Various Arecanut Diseases using Image Processing and Machine Learning Approaches,” International Journal of Engineering Research & Technology (IJERT), vol. 9, no. 8, 2020. 

[2] S. B. Mallikarjuna et al., “CNN Based Method for Multi-Type Diseased Arecanut Image Classification,” International Journal of Innovative Technology and Exploring Engineering (IJITEE), 2021. 

[3] P. Shetty et al., “ArecaShield: AI Powered Arecanut Disease Detection and Advisory System,” in Proc. IEEE Int. Conf., 2023. 

[4] D. Sharma, “Artificial Intelligence in Agriculture,” Int. J. Advanced Science and Technology, vol. 29, no. 6, 2020. 

[5] R. Dhanapal et al., “Crop Price Prediction using Supervised Machine Learning Algorithms,” in Proc. Int. Conf. Computing and Communication Technologies, 2021. 

[6] “Machine Learning and IoT-Based Smart Farming for Enhancing the Crop Yield,” in Proc. Int. Conf. Smart Systems, 2022. 

[7] P. Balanagouda et al., “Phytophthora Diseases of Arecanut in India: Prior Findings, Present Status and Future Prospects,” Journal of Plantation Crops, vol. 47, no. 2, pp. 85–95, 2019. 

[8] K. M. Sabu and T. K. Manoj Kumar, “Predictive Analytics in Agriculture: Forecasting Prices of Arecanuts in Kerala,” Int. J. Engineering Research & Technology, vol. 7, no. 5, 2018. 

[9] K. G. Liakos et al., “Machine Learning in Agriculture: A Review,” Sensors, vol. 18, no. 8, p. 2674, 2018, doi: 10.3390/s18082674. 

[10] R. Bhat and S. Sujatha, “Soil Fertility Status as Influenced by Arecanut Based Cropping System and Nutrient Management,” Journal of Plantation Crops, vol. 31, no. 2, pp. 102–108, 2003. 

[11] G. C. Acharya et al., “Effect of Organic and Inorganic Sources of Nutrients on Soil Fertility Status of Arecanut (Areca catechu L.),” Journal of Plantation Crops, vol. 45, no. 3, pp. 235–240, 2017. 

[12] K. M. Sunil et al., “Influence of Weather Parameters on Yield and Yield Attributes of Areca Nut (Areca catechu L.),” Journal of Agrometeorology, vol. 9, no. 2, pp. 152–156, 2007. 

[13] R. Vasundhara et al., “Characterisation and Classification of Arecanut-Growing Soils of Karnataka, India,” Agropedology, vol. 24, no. 1, pp. 45–52, 2014. 

[14] V. Upadhyay and E. P. Devi, “Diseases of Arecanut and their Management,” Agricultural Reviews, vol. 36, no. 2, pp. 138–144, 2015. 

[15] A. K. Kumar et al., “Forecasting Areca Nut Market Prices Using the ARIMA Model: A Case Study of India,” Int. J. Applied Engineering Research, vol. 14, no. 10, pp. 2456–2462, 2019. 

[16] K. Rajashree et al., “Prediction of Fruit Rot Disease Incidence in Arecanut Based on Weather Parameters,” in Proc. Int. Conf. Data Science and AI, 2021. 

[17] A. Hegde et al., “Identification and Categorization of Diseases in Arecanut: A Machine Learning Approach,” in Proc. Int. Conf. AI and Smart Systems, 2022. 

[18] F. D. Shadrach et al., “Efficient Deep Learning Framework for Arecanut Disease Detection Using Graph Neural Network and Bat Algorithm,” in Proc. IEEE Int. Conf., 2023. 

[19] S. C. Siddalingadevaru et al., “Disease Diagnosis and Sustainable Prevention in Arecanut Farming,” in Proc. Int. Conf. Electronics and Renewable Systems (ICEARS), 2025. 

[20] A. M. G. Anilkumar et al., “Detection of Diseases in Arecanut Using Convolutional Neural Networks,” Int. Res. J. Engineering and Technology (IRJET), vol. 8, no. 5, pp. 4282–4286, 2021. 



### **Personal Profile** 



**Dr.Thyagaraju G S,** Prof. and Head of Dept Project Guide 









**Dr. Thyagaraju G S** has completed his M.Tech in the year 2002, from University of Mysore and PhD in the year 2014 from VTU Belagavi. His areas of interest are Artificial Intelligence, Quantum Computing and Theory of Mind. He has published 52 international research papers and authored 3 Books 

###### Email ID: profthyagu@gmail.com 

Name: Sathwik Hebbar P 

USN: 4SU23CS088 

Address: Narga House,Kalmanja Village and Post, Belthangady Taluk,Dakshina Kannada District E-mail ID: sathwikhebbarap@gmail.com Contact Phone No: 6361176720 

###### Name: Suchesh S shetty 

USN: 4SU23CS102 

Address: Pratiksha Nilaya, Kuvempu Nagara,Belal Road,Ujire,Belthangady Taluk,Dakshina Kannada District 

E-mail ID: sucheshshetty@gmail.com Contact Phone No: 8310201271 

###### Name: Vihar A C 

USN: 4SU23CS122 

Address: Adkadakare House,Kadirudyavara Village and Post,Belthangady Taluk,Dakshina Kannada District 

E-mail ID:  viharac717@gmail.com Contact Phone No:  7760094937 

###### Name: Samarth N K 

###### USN: 4SU23CS083 

Address: Badyar House,Padangady Village and Post,Belthangady Taluk,Dakshina Kannada District E-mail ID: samarthsamarth32005@gmail.com Contact Phone No: 8762367699 

