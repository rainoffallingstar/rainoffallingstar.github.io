---
layout: mypost
title: 2022-11-04-Workflow Machine Learning with Radio-mics
categories: [workflow]
---

### **Workflow：Machine Learning with Radio-mics**

Yanhua Zheng^[1]，Teng Zuo^[1], Lingfeng He^[1]

^ [1] Gmade Studio(排名不分前后)

1. 收集按金标准（病理/基因等）明确诊断的患者信息（去除可识别的身份信息），包括ct号、性别、年龄及其他必要临床检验数据。（注意：多采集定量资料，少采集分类变量，在这一方面，尽量使用可以确定分类标准的定量资料进行代替。）

2. 收集患者ct图像，使用itk-snap/3d slicer进行阅片，结合报告裁剪肾脏+肿瘤总体，以”患者编号+nii.gz“保存到该ct图像下的ROI文件夹，此后导出每个层次的肿瘤图像，保存为”图像标号+tiff“在该CT图像下的output文件夹（注意：忽略过采样问题，在肿瘤末端的伪影不作采集， 在采集过程中使用统一阅片工具及相关设置，如窗位和窗宽）。

3. 使用python/R 进行图像特征提取，与必要患者临床信息一起保存为csv文件。可参考Heidelberg university 开发的Image Data Explorer v1.3.2平台。

4. 在表格数据的基础上按8：2的比例划分训练集及测试集，使用lasso方法进行最优子集的选择。

5. 经典机器学习建模遵循从低光滑度向高光滑度发展的选择，使用mlr3包，依次进行逻辑斯蒂回归、LDA、决策树、支持向量机等模型建模并测试。

6. 神经网络（mlr3包或tensorflow包)建模：在最优变量子集下建模并测试，使用mlr3包自动建模确定最佳网络层数及构架，后使用tensorflow包进行复刻并提取训练过程（如需要的话），测试在最优变量子集下的模型效能，如效能较低，手动选择增加变量数再次测试。

7. 保留各模型最佳测试结果和权重，计算混淆矩阵、AUC值并画出混淆矩阵及ROC图。确定最佳模型及效能。