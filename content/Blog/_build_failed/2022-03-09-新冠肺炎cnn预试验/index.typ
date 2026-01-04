#import "../../../config.typ": template, tufted
#show: template.with(title: "新冠肺炎CNN预试验").with(lang: "en")

== 2022-03-09-新冠肺炎CNN预试验

=== 目的

+ 搭建一套可行的提取肺炎影像学特征的神经网络模型。

+ 通过学习病毒性肺炎、社区获得性肺炎的特征，减少在拟合小数据样本的CMV肺炎时的训练时长及过拟合的概率。

=== 方法

+ 建立图像数据库：获取单中心开源的肺部CT图像，所有CT图像及诊断均由影像科医生审核并参考临床资料（CPR、痰培养等）给出标签。共收录社区获得性肺炎（CAP）4800张，新冠肺炎（covid19）13680张，正常肺CT图像11405张。分别随机抽取5000张新冠肺炎、正常肺CT与社区获得性肺炎组成平衡数据集，按照8：1：1的比例随机抽取组成训练集、验证集、测试集。

+ 模型搭建与预训练：基于Tensorflow2.4 实现了经典mobilenet模型，并实现tensorboard可视化。集成在IMAGEnet数据集下预训练的模型。
   
   
   
   Table 3
   
   The structure of MobileNet v2
   
   | Layer(Funtions)               | Output Shape    | Stride | Filter shape      |
   | ----------------------------- | --------------- | ------ | ----------------- |
   | Input Layer                   | None,256,256,3  | /      | /                 |
   | Conv1 (Conv+BN+ReLU6)         | None,128,128,32 | 2      | 3 _3 _32          |
   | inverted_residual (Linear)    | None,128,128,16 | 1      | 1 _1 _32 _16      |
   | inverted_residual_1 (ReLU6)   | None,64,64,24   | 2      | 3 _ 3 _16 _24     |
   | inverted_residual_2 (Linear)  | None,64,64,24   | 1      | 1_1 _24           |
   | inverted_residual_3 (ReLU6)   | None,32,32,32   | 2      | 3 _ 3 _24 _32     |
   | inverted_residual_4 (Linear)  | None,32,32,32   | 1      | 1_1 _32           |
   | inverted_residual_5 (Linear)  | None,32,32,32   | 1      | 1_1 _32           |
   | inverted_residual_6 (ReLU6)   | None,16,16,64   | 2      | 3_3_32_64         |
   | inverted_residual_7 (Linear)  | None,16,16,64   | 1      | 1_1 _64           |
   | inverted_residual_8 (Linear)  | None,16,16,64   | 1      | 1_1 _64           |
   | inverted_residual_9 (Linear)  | None,16,16,64   | 1      | 1_ 1_64           |
   | inverted_residual_10 (Linear) | None,16,16,96   | 1      | 1  _ 1 _64_96     |
   | inverted_residual_11 (Linear) | None,16,16,96   | 1      | 1_1 _96           |
   | inverted_residual_12 (Linear) | None,16,16,96   | 1      | 1_ 1_96           |
   | inverted_residual_13 (ReLU6)  | None,8,8,160    | 2      | 3_3 _96 _160      |
   | inverted_residual_14 (Linear) | None,8,8,160    | 1      | 1_1 _160          |
   | inverted_residual_15 (Linear) | None,8,8,160    | 1      | 1_1 _160          |
   | inverted_residual_16 (Linear) | None,8,8,320    | 1      | 1_1_160_320       |
   | Conv (ReLU6)                  | None,8,8,1280   | 1      | 1_1_320_1280      |
   | Global average pooling        | None,1280       | 1      | Pool 8_8          |
   | Dropout                       | None,1280       | 1      | Probability = 0.2 |
   | Clssifier(ReLU)               | None,2          | /      | Classifier        |
   
   !#link("model.png")[这是图片]
+ 正式训练：将预训练模型删除分类层，将训练集、验证集向量化，输入模型，初始学习率设置为1e-4，采用adam算法优化学习率，设置分类数为3，最大epoch为30。训练在云端一台搭载了tensorflow2.4的RTX2080ti（10G显存）、6_E5cpu的服务器内实现。默认保存在验证集上表现最优的模型权重。

+ 测试模型效能：在测试集上进行模型能力测试，计算准确率、召回率、正确率、假阳性率、F1分数等评价指标，绘出ROC曲线并计算曲线下面积。

=== 结果

MobilenetV2在epoch 22达到train acc 0.98，train loss 0.02；val acc 0.99，val loss 0.04，停止训练,训练过程未见过拟合。

!#link("acc.png")[这是图片]

!#link("loss.png")[这是图片]

Table 2

| 类别      | 精确率 | 召回率  | FPR  | F1score |
| ------- | --- | ---- | ---- | ------- |
| covid19 | 91% | 100% | 9.7% | 98%     |

Auc=0.998!#link("auc.jepg")[这是图片]
