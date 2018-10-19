import neuralnet as nn
import numpy as np
import csv
import ag

nf = nn.NeuralFactory()
nn_obj = nf.create(hidden_actv_fcn=nn.ActivationFcn(), final_actv_fcn=nn.ActivationFcn(),
                   layers_sizes=[6, 3], input_size=4)

with open("../dataset/iris.data") as csv_file:
    CSV_READER = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
    DATA = []
    for row in CSV_READER:
        DATA.append(row)
    DATA.pop()
DATA = np.array(DATA, dtype=np.float64)

# Média zero
DATA[:, 0] = DATA[:, 0] - np.mean(DATA[:, 0])
DATA[:, 1] = DATA[:, 1] - np.mean(DATA[:, 1])
DATA[:, 2] = DATA[:, 2] - np.mean(DATA[:, 2])
DATA[:, 3] = DATA[:, 3] - np.mean(DATA[:, 3])

# Variância 1
DATA[:, 0] = DATA[:, 0] / np.std(DATA[:, 0])
DATA[:, 1] = DATA[:, 1] / np.std(DATA[:, 1])
DATA[:, 2] = DATA[:, 2] / np.std(DATA[:, 2])
DATA[:, 3] = DATA[:, 3] / np.std(DATA[:, 3])

y_array = DATA[:, 4:]
y_array = [int(y[0]) for y in y_array]
y = np.zeros((len(y_array), 3), dtype=int)
y[np.arange(len(y_array)), y_array] = 1
x = DATA[:, :4]

# nn_obj.fit(x_array=DATA[:, :4], y_array=DATA[:, 4:], epochs=1000, n=0.1)
factory_args = [nn.ActivationFcn(), nn.ActivationFcn(), [6, 3], 4]
pop = ag.Population(factory=nn.NeuralFactory(), factory_args=factory_args,
                    pop_size=10, individuals=None)

pop.test_pop(input_array=x, y_array=y)
