import numpy as np
import pickle


class NeuralNet:
    def __init__(self, layers):
        self.layers = layers

    def save_neural_net(self, where):
        with open(where, 'wb') as out_file:
            pickle.dump(self, out_file, pickle.HIGHEST_PROTOCOL)

    def predict(self, input_array):
        result = input_array.copy()
        for i in range(self.layers.shape[0]):
            result = self.layers[i].feed_foward(result)
        return result

    def evaluate(self, input_array, y_array):
        result = self.predict(input_array=input_array)
        return 1 if y_array[np.argmax(result)] == 1 else 0
        # return 1 / (1 + np.sum(np.abs(np.subtract(result, y_array))))

    def fit_predict(self, input_array):
        actv_values = np.zeros(len(self.layers) + 1, dtype=np.ndarray)
        actv_values[0] = np.array(input_array, dtype=float)
        for i in range(self.layers.shape[0]):
            actv_values[i + 1] = self.layers[i].feed_foward(actv_values[i])
        return actv_values[1:]

    # Endireitar essa função na parte de avaliação do erro
    def fit(self, x_array, y_array, epochs, n):
        deltas = np.zeros(len(self.layers), dtype=np.ndarray)
        for e in range(epochs):
            predictions = [np.array(self.fit_predict(x), dtype=np.ndarray) for x in x_array]
            rights = 0
            for p in range(len(predictions)):
                print('y = ' + str(y_array[p][0]))
                print('predict = ' + str(predictions[p][-1]))

                rights += 1 if np.argmax(predictions[p][-1]) == y_array[p] else 0
                y = np.zeros(3)
                y[int(y_array[p])] = 1
                deltas[-1] = np.multiply(np.subtract(y, predictions[p][-1]),
                                         self.layers[-1].activation_fcn.grad(predictions[p][-1]))

                for l in range(len(self.layers) - 2, -1, -1):
                    deltas[l] = np.multiply(np.matmul(self.layers[l + 1].weight_mtr[1:, :], deltas[l + 1]),
                                            self.layers[l].activation_fcn.grad(predictions[p][l]))

                input_with_bias = np.append(1, x_array[p])
                for i in range(self.layers[0].weight_mtr.shape[0]):
                    for j in range(self.layers[0].weight_mtr.shape[1]):
                        self.layers[0].weight_mtr[i][j] = self.layers[0].weight_mtr[i][j] + \
                            (n * deltas[0][j] * input_with_bias[i])

                for l in range(1, len(self.layers)):
                    mtr = self.layers[l].weight_mtr
                    input_with_bias = np.append(1, predictions[p][l - 1])
                    for i in range(mtr.shape[0]):
                        for j in range(mtr.shape[1]):
                            mtr[i][j] = mtr[i][j] + (n * deltas[l][j] * input_with_bias[i])

            print('epoch = ' + str(e))
            print('acc = ' + str(rights / len(predictions)))
            print('\n')


class NeuralLayer:
    def __init__(self, number_of_neurons, actv_fcn, input_size):
        self.activation_fcn = actv_fcn
        self.number_of_neurons = number_of_neurons
        self.input_size = input_size
        self.weight_mtr = np.random.uniform(-1, 1, (self.input_size + 1, self.number_of_neurons))

    def feed_foward(self, input_array):
        return self.activation_fcn.actv(np.matmul(np.append(1, input_array), self.weight_mtr))


class NeuralFactory:
    def __init__(self):
        pass

    def create(self, hidden_actv_fcn, final_actv_fcn, layers_sizes, input_size):
        num_layers = len(layers_sizes)
        layers = np.zeros(num_layers, dtype=np.ndarray)
        layers[0] = NeuralLayer(layers_sizes[0], hidden_actv_fcn, input_size)
        for i in range(1, num_layers - 1):
            layers[i] = NeuralLayer(layers_sizes[i], hidden_actv_fcn, layers_sizes[i - 1])
        layers[num_layers - 1] = NeuralLayer(layers_sizes[-1],
                                             final_actv_fcn, layers_sizes[-2])

        return NeuralNet(layers)


class ActivationFcn:
    def __init__(self):
        pass

    def actv(self, val_array):
        return np.divide(1, np.add(1, np.exp(-val_array)))

    def grad(self, val_array):
        return np.multiply(val_array, np.subtract(1, val_array))


def load_neural_net(where):
    with open(where, 'rb') as in_file:
        return pickle.load(in_file)
