# data analysis and wrangling
import pandas as pd
import numpy as np
from progressbar import ProgressBar
from mydataset.mydataset import MyDataSet,cleanLogdir

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# machine learning
import tensorflow as tf
from sklearn.model_selection import train_test_split


#=======================自定义函数====================================

#用于初始化权重和偏置项
def weight_variable(shape,name=None):
  initial = tf.truncated_normal(shape, stddev=0.1) #正态分布随机
  return tf.Variable(initial,name=name)

def bias_variable(shape,name=None):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial,name=name)

# 判断预测的精准程度
def accuracy(predictions, labels):
    predictions = predictions > 0.5
    return (np.sum(predictions == labels) / predictions.shape[0])


def getLable(batch):
    return batch.iloc[:,1].values.reshape(batch.shape[0],1)

def getFeatures(batch):
    return batch.iloc[:,2:].values

#=======================读取数据====================================
cleanLogdir('mnist_logs')
train_set = MyDataSet('../data/train.csv',header=0)
challange = MyDataSet('../data/test.csv',header=0)

ids = challange.data.iloc[:,0].values
final = pd.DataFrame({
    'id': ids,
    'target': np.zeros(ids.shape[0])
})

#=======================TensorFlow==================================


#每层节点数
hidden_nodes_1 = 57  #num of features
hidden_nodes_2 = 100
hidden_nodes_3 = 100
output_nodes = 1





beta =0.01

sess = tf.Session(config=tf.ConfigProto(device_count={'gpu':0}))


#占位符,运行时由实际数据替代
x = tf.placeholder(dtype="float64",shape=[None,hidden_nodes_1],name="Input")
y_ = tf.placeholder(dtype="float64",shape=[None,output_nodes],name="Lable")

#定义每层的weight 与 bias
#weight使用truncated_normal(截断正态随机)初始化,bias填充0
weight1 = tf.Variable(tf.truncated_normal([hidden_nodes_1,hidden_nodes_2],dtype=tf.float64),name="W1")
biases1 = tf.Variable(tf.zeros([hidden_nodes_2],dtype=tf.float64),name="B1")
m1 = tf.matmul(x,weight1)+biases1  #数据入口x
res1 = tf.nn.relu(m1)

weight2 = tf.Variable(tf.truncated_normal([hidden_nodes_2, hidden_nodes_3], dtype=tf.float64),name="W2")
biases2 = tf.Variable(tf.zeros([hidden_nodes_3],dtype=tf.float64),name="B2")
m2 = tf.matmul(res1,weight2)+biases2
res2 = tf.nn.relu(m2)

weight3 = tf.Variable(tf.truncated_normal([hidden_nodes_3, output_nodes], dtype=tf.float64),name="W3")
biases3 = tf.Variable(tf.zeros([output_nodes],dtype=tf.float64),name="B3")
res3 = tf.matmul(res2,weight3)+biases3

regularizers = tf.nn.l2_loss(weight1)+tf.nn.l2_loss(weight2)+tf.nn.l2_loss(weight3)
loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=res3,labels=y_,name="Cost")) #结果出口y
loss = tf.reduce_mean(loss+beta*regularizers)
y = tf.nn.sigmoid(res3)

optimizer = tf.train.GradientDescentOptimizer(0.001).minimize(loss)

tf.summary.scalar("Cost", loss)  # 持久化一个标量Cost
merged = tf.summary.merge_all()
summary_writer = tf.summary.FileWriter('../mnist_logs', sess.graph)



sess.run(tf.global_variables_initializer())  # 初始化变量
print('Initialized')

step_length = 10000
Train_times = 200000
print("Step_length: %d, Train_times: %d" % (step_length, Train_times))


with ProgressBar() as bar:
    print("Brgin fast training:")
    for i in bar(range(Train_times)):
        # 随机抓取训练数据中的100个批处理数据点，然后用这些数据点作为参数替换之前的占位符(x,y_)来运行train_step
        # 而非每次都将所有数据作为趋近目标
        batch = train_set.getNextBatch(step_length)
        _,summary=sess.run([optimizer,merged], feed_dict={x: getFeatures(batch), y_: getLable(batch)})
        summary_writer.add_summary(summary, i)
        # if(i%(Train_times/10)==0):
        #     test_batch = train_set.getNextBatch(step_length)
        #
        #     predict = sess.run(y,feed_dict={x:getFeatures(test_batch)})
        #     print('Training accuracy: %f' % accuracy(predict, getLable(test_batch)))
        #

final_prediction  = sess.run(y,feed_dict={x:challange.data.iloc[:,1:].values})
final["target"] = final_prediction
final.to_csv("prediction.csv", index=False)