# Introduction

Title: The Improvement of Adaptive Data Rate Algorithm for LoRaWAN

Author: Fang-Kuei Chiu (I-Shou University)

Advisor: Dr. Guan-Hsiung Liaw

# Abstract

　　LPWA (Low-Power Wide-Area) is a type of wireless communication technology for IoT (Internet of Things). These technologies can transmit data with low power, low cost and long range. Because of these attributes, LPWA technologies can be exploited in variety of applications, such as smart city, smart metering, agriculture, environmental monitoring, etc. With the progress of LPWA technologies, the number of nodes in the network will increase heavily and rapidly. It is important for how well these technologies will scale as the number of nodes grows.

　　In LoRaWAN, adaptive data rate (ADR) mechanism can improve the network capacity by adjusting the spreading factor (SF) to change the data rate. Recently, several studies have proposed some algorithms to optimize the ADR strategy and achieved the results better than basic ADR strategy in the simulation. However, most variants of ADR strategy only were evaluated in single-gateway sceranio. Few of them took multiple gateways into consideration. In multiple-gateway sceranio, the distance among different gateways will make the overlapping areas in the receiving range exist, and then affect the network performance. In this thesis, based on these variants of ADR strategy, several improved variants are proposed for multiple-gateway sceranio. They can effectively treat the end-devices located in the overlapping areas. The effectiveness of the proposed methods will be evaluated by simulations.

Keywords： Internet of Things, Low-Power Wide-Area Network, LoRaWAN, Adaptive Data Rate, Spreading Factor


# Simulator

LoRaSim: https://www.lancaster.ac.uk/scc/sites/lora/lorasim.html

# Reference

[1]	L. Atzori, A. Iera, and G. Morabito, “The internet of things: A survey,” Comput. Netw., vol. 54, no. 15, pp. 2787–2805, 2010.

[2]	International Telecommunication Union. Accessed on June 14, 2019. [Online]. Available: https://www.itu.int/en/Pages/default.aspx

[3]	I. Peña-López, Strategy and Policy Unit of International Telecommunications Union, Geneva, Switzerland: ITU Internet Reports, 2005.

[4]	“Cellular networks for massive IoT: Enabling low power wide area applications,” Ericsson, Stockholm, Sweden, Tech. Rep. UEN 284 23-3278, Jan. 2016. [Online]. Available: https://www.ericsson.com/res/docs/whitepapers/wp_iot.pdf

[5]	IoT Analytics. Accessed on June 14, 2019. [Online]. Available: https://iot-analytics.com/

[6]	K. Lueth, “State of the IoT 2018: Number of IoT devices now at 7B – Market accelerating,” IoT Analytics, Aug. 8, 2018. [Online]. Accessed on Jun 16, 2019.  Available: https://iot-analytics.com/state-of-the-iot-update-q1-q2-2018-number-of-iot-devices-now-7b/

[7]	ABI Research. Accessed on June 14, 2019. [Online]. Available: https://www.abiresearch.com/

[8]	O. Bay, “NB-IoT, CAT-M, SIGFOX and LoRa Battle for Dominance Drives Global LPWA Network Connections to Pass 1 Billion By 2023,” ABI Research, New York, Jun. 11, 2018. [Online]. Accessed on Jun 16, 2019. Available: https://www.abiresearch.com/press/nb-iot-cat-m-sigfox-and-lora-battle-dominance-drives-global-lpwa-network-connections-pass-1-billion-2023/

[9]	E. Pasqua, “LPWAN emerging as fastest growing IoT communication technology – 1.1 billion IoT connections expected by 2023, LoRa and NB-IoT the current market leaders,” IoT Analytics, Sep. 27, 2018. [Online]. Accessed on Jun 16, 2019.  Available: https://iot-analytics.com/lpwan-market-report-2018-2023-new-report/

[10]	T. Niwa, “LPWA market is still in early stage,” Techno Systems Research, Oct. 11, 2018. [Online]. Accessed on Jun 16, 2019.  Available: https://www.advantech.com/resources/news/7041a966-7328-4702-ac7d-ffcd9609cccc

[11]	LoRa Alliance, “About LoRaWAN,” [Online]. Accessed on Jun 20, 2019. Available: https://lora-alliance.org/about-lorawan

[12]	LoRa Alliance, “A technical overview of LoRa and LoRaWAN,” White Paper, 2015.

[13]	M. Bor, J. E. Vidler, and U. Roedig, “LoRa for the Internet of Things,” 2016.

[14]	A. Augustin, “A study of LoRa: Long range & low power networks for the internet of things,” Sensors, vol. 16, no. 9, p. 1466, 2016.

[15]	T. Voigt, M. Bor, U. Roedig, and J. Alonso, “Mitigating inter-network interference in LoRa networks,” arXiv preprint arXiv:1611.00688, 2016.

[16]	J. Petäjäjärvi, K. Mikhaylov, A. Roivainen, T. Hanninen, and M. Pettissalo, “On the coverage of LPWANs: range evaluation and channel attenuation model for LoRa technology,” in 2015 14th International Conference on ITS Telecommunications (ITST), 2015, pp. 55–59.

[17]	J. Petäjäjärvi, K. Mikhaylov, M. Hämäläinen, J. Iinatti, "Evaluation of LoRa LPWAN technology for remote health and wellbeing monitoring", Proc. 10th Int. Symp. Med. Inf. Commun. Technol. (ISMICT), pp. 1-5, Mar. 2016.

[18]	J. de Carvalho Silva, J. J. P. C. Rodrigues, A. M. Alberti, P. Solic, and A. L. L. Aquino, “LoRaWAN - A low power WAN protocol for Internet of Things: A review and opportunities,” in 2017 2nd International Multidisciplinary Conference on Computer and Energy Science (SpliTech), 2017, pp. 1–6.

[19]	F. Adelantado, X. Vilajosana, P. Tuset-Peiro, B. Martinez, and J. Melia,” Understanding the limits of LoRaWAN,” IEEE Communication Magazine, 2017, to appear, arXiv preprint arXiv:1607.08011.

[20]	G. Ferre, "Collision and packet loss analysis in a LoRaWAN network", Proc. Eur. Signal Process. Conf. (EUSIPCO), pp. 2586-2590, 2017.

[21]	J. Petäjäjärvi, K. Mikhaylov, M. Pettissalo, J. Janhunen, J. Iinatti, "Performance of a low-power wide-area network based on LoRa technology: Doppler robustness scalability and coverage", Int. J. Distrib. Sensor Netw., vol. 13, no. 3, pp. 1-16, 2017

[22]	D. Bankov, E. Khorov, and A. Lyakhov, “Mathematical model of LoRaWAN channel access,” in Proceedings of the IEEE 18th International Symposium on A World of Wireless, Mobile and Multimedia Networks (WoWMoM), Macao, China, 2017, pp. 12–15.

[23]	K. Mikhaylov, J. Petäjäjärvi, and T. H¨anninen, “Analysis of capacity and scalability of the lora low power wide area network technology,” in 22th European Wireless Conference, May 2016, pp. 1–6.

[24]	O. Georgiou and U. Raza, “Low power wide area network analysis: Can lora scale?” IEEE Wireless Communications Letters, 2017.

[25]	M. C. Bor, U. Roedig, T. Voigt, and J. M. Alonso, “Do LoRa Low-Power Wide-Area Networks Scale?” in 19th ACM Int. Conf. on Modeling, Analysis and Simulation of Wireless and Mobile Systems, ser. MSWiM ’16, 2016, pp. 59–67.

[26]	D. Magrin, M. Centenaro, L. Vangelista, "Performance Evaluation of LoRa Networks in a Smart City Scenario", IEEE ICC 2017 SAC Symposium Internet of Things Track (ICC'17), pp. 1-5, 2017.

[27]	N. Varsier, J. Schwoerer, "Capacity limits of Lo-Ra Wan technology for smart metering applications", Communications (ICC) 2017 IEEE International Conference on, pp. 1-6, 2017.

[28]	F. Van den Abeele, J. Haxhibeqiri, I. Moerman, and J. Hoebeke, “Scalability analysis of large-scale LoRaWAN networks in ns-3,” IEEE Internet of Things Journal, vol. 4, no. 6, pp. 2186–2198, 2017.

[29]	S. Muratchaev, A. Bakhtin, A. Volkov, V. Ivanov, and A. Baskakov, “Modeling the process of network scaling for LoRaWan basen on NS3,” in Young Researchers in Electrical and Electronic Engineering (EIConRus), 2018 IEEE Conference Russian, 2018, pp. 1309–1312.

[30]	B. Reynders, W. Meert, S. Pollin, "Power and spreading factor control in low power wide area networks", IEEE ICC 2017 SAC Symposium Internet of Things Track (ICC'17), pp. 1-5, 2017.

[31]	K. Q. Abdelfadeel, V. Cionca, and D. Pesch, “Fair Adaptive Data Rate Allocation and Power Control in LoRaWAN,” arXiv preprint arXiv:1802.10338, 2018.

[32]	V. Hauser, “Proposal of Adaptive Data Rate Algorithm for LoRaWAN-Based Infrastructure,” in Future Internet of Things and Cloud (FiCloud), 2017 IEEE 5th International Conference on, 2017, pp. 85–90.

[33]	F. Cuomo, M. Campo, A. Caponi, G. Bianchi, G. Rossini, and P. Pisani, “EXPLoRa: Extending the performance of LoRa by suitable spreading factor allocations,” in Wireless and Mobile Computing, Networking and Communications (WiMob), 2017, pp. 1–8.

[34]	F. Cuomo et al., “Towards traffic-oriented spreading factor allocations in LoRaWAN systems,” in 2018 17th Annual Mediterranean Ad Hoc Networking Workshop (Med-Hoc-Net), 2018, pp. 1–8.

[35]	Bluetooth. Accessed on June 14, 2019. [Online]. Available: https://www.bluetooth.com/

[36]	Zigbee Alliance. Accessed on June 14, 2019. [Online]. Available: https://www.zigbee.org/

[37]	Wi-Fi Alliance. Accessed on June 14, 2019. [Online]. Available: https://www.wi-fi.org/

[38]	3GPP, “LTE-Advanced.” Accessed on June 14, 2019. [Online]. Available: https://www.3gpp.org/technologies/keywords-acronyms/97-lte-advanced

[39]	U. Raza, P. Kulkarni, and M. Sooriyabandara, “Low Power Wide Area Networks: An Overview,” IEEE Communications Surveys Tutorials, vol. 19, no. 2, pp. 855–873, 2017.

[40]	3GPP, “Standardization of NB-IOT completed.” Accessed on June 14, 2019. [Online]. Available: https://www.3gpp.org/news-events/1785-nb_iot_complete

[41]	Sigfox. Accessed on June 14, 2019. [Online]. Available: https://www.sigfox.com/en

[42]	Semtech, “What is LoRa?” Accessed on June 14, 2019. [Online]. Available:  https://www.semtech.com/lora/what-is-lora

[43]	Ingenu, “RPMA Technology.” Accessed on June 14, 2019. [Online]. Available: https://www.ingenu.com/technology/rpma/

[44]	Weightless, “What is Weightless?” Accessed on June 14, 2019. [Online]. Available: http://www.weightless.org/about/what-is-weightless

[45]	LoRa Alliance. Accessed on June 14, 2019. [Online]. Available: https://lora-alliance.org/

[46]	3GPP. Accessed on June 14, 2019. [Online]. Available: https://www.3gpp.org/

[47]	LoRa Alliance, “A technical overview of LoRa and LoRaWAN,” White Paper, 2015.

[48]	K. Mekki, E. Bajic, F. Chaxel, F. Meyer, "A comparative study of LPWAN technologies for large-scale IoT deployment", ICT Exp., Jan. 2018.

[49]	LORIOT.io. Accessed on May 30, 2018 [Online]. Available: https://www.loriot.io/lorawan.html

[50]	Semtech SX1272 Datasheet, March 2018, [Online] Available: http://www.semtech.com/images/datasheet/sxI272.pdf.

[51]	JPL's Wireless Communication Reference Website. Accessed on May 30, 2018 [Online]. Available: http://www.wirelesscommunication.nl/reference/chaptr06/aloha/aloha.htm

[52]	LoRa Alliance, “LoRaWAN specification v1.0.3.” 2017, [online] Available: https://lora-alliance.org/sites/default/files/2018-07/lorawan1.0.3.pdf

[53]	LoRa Alliance, “LoRaWAN Regional Parameters v1.1rB.” 2017, [online] Available: https://loraalliance.org/sites/default/files/2018-04/lorawantm_regional_parameters_v1.1rb_-_final.pdf

[54]	NS-3. Accessed on: May 20, 2018. [Online]. Available: https://www.nsnam.org/

[55]	LoRaSim. Accessed on May 20, 2018. [Online]. Available: https://www.lancaster.ac.uk/scc/sites/lora/lorasim.html

[56]	Matlab. Accessed on May 20, 2018. [Online]. Available: https://www.mathworks.com/products/matlab.html

[57]	SimPy. Accessed on May 20, 2018. [Online]. Available: https://simpy.readthedocs.io/en/latest/
