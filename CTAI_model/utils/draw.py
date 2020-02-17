import matplotlib.pyplot as plt
import numpy as np

data = []
data_true = []
with open('../result/0.50nohup50.txt', 'r') as f:
    data = [i.replace('\n', '') for i in f.readlines()]

for i in range(len(data)):
    if i % 3 == 0:
        x = data[i].split(' ')
        data_true.append([x[2].replace('test', '').replace('train_loss:', ''), x[-1]])

print(data_true)

ax = plt.gca()

plt.rcParams['savefig.dpi'] = 300  # 图片像素
plt.rcParams['figure.dpi'] = 200  # 分辨率

# plt.plot(range(1,51), np.squeeze([i[0] for i in data_true]), label='Train loss')
# plt.ylabel('loss')
# plt.xlabel('epochs')
# plt.title("Model: train loss")
# plt.legend()
# plt.show()
ax.invert_yaxis()

plt.plot(range(1, 51), np.squeeze([i[0] for i in data_true]), label='Train loss')
plt.ylabel('loss')
plt.xlabel('epochs')
plt.title("Model: train loss")
plt.legend()
# plt.show()

plt.savefig('plot123_2.png', dpi=200)  # 指定分辨率保存
