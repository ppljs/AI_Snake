import numpy as np
from sklearn.metrics import mean_squared_error as mqe
np.set_printoptions(precision=2)

TAM_POP = 20
TAX_MUT = 0.1
NUM_LAYERS = 2
LAYERS_SIZES = [2,1]
FEATURE_QTY = 1
MAXX = 1
G = 1

def math_functions(data, func_name):
    if func_name == 'square':
        return [a*a+5 for a in data]
    if func_name == 'relu':
        return np.maximum(data, 0)
    if func_name == 'tanh':
        return np.tanh(data)
    if func_name == 'linear':
        return np.array(data)
    if func_name == 'sigmoid':
        data = np.array(data)
        result = np.empty(data.shape)
        for i in range(data.shape[0]):
            result[i] = 1.0 / (1.0 + np.exp(-data[i]))
        return result
    return None

def create_neural_net(num_layers, layers_sizes, feature_qty):
    neural_net = np.zeros(num_layers, dtype=np.ndarray)
    neural_net[0] = np.random.uniform(-1, 1, (feature_qty + 1, layers_sizes[0]))

    for i in range(1, num_layers):
        neural_net[i] = np.random.uniform(-1, 1, (layers_sizes[i - 1] + 1, layers_sizes[i]))
    return neural_net

def predict(neural_net, features, activation_func):
    num_layers = neural_net.shape[0]
    result = np.array(np.append(features, 1))
    for i in range(num_layers):
        result = np.matmul(result, neural_net[i])
        result = math_functions(result, activation_func)
        result = np.append(result, 1)
    result = np.delete(result, -1)
    return result

def init_pop():
    ind = np.zeros(TAM_POP, dtype=np.ndarray)
    for i in range(TAM_POP):
        ind[i] = create_neural_net(NUM_LAYERS, LAYERS_SIZES, FEATURE_QTY)
    return ind

def avaliation(ind, features, y_data):
    fit = np.zeros(TAM_POP)
    # Temp array used to recive the predicted values from the neural network.
    predict_temp = np.zeros(len(features))
    for i in range(TAM_POP):  # For each neural network.
        for j in range(len(features)):  # For each value to be predicted.
            predict_temp[j] = predict(ind[i], features[j], 'relu')
        # Calculates fit using the mean square error function of the predicted values and the correct values.
        fit[i] = 1+1/mqe(predict_temp, y_data)

    print('Correct Data:\n', *y_data, '\n\n')
    print('Data from Neural Network:\n', predict_temp)
    return fit

def crossover(ind, fit):
    maxfit = fit[0]
    maxi = 0
    for i in range(1, TAM_POP):  # Search for the best. We don't kill the best!
        if fit[i] > maxfit:
            maxfit = fit[i]
            maxi = i

    for i in range(0, TAM_POP):
        if i == maxi:
            continue  # Protect the best.
        # Crossover
        ind[i] = (ind[i] + ind[maxi])/2  # Using arithmetic mean.
    # Mutation
    ind[i] = ind[i] + ((np.random.uniform(-1, 1) % MAXX-(MAXX/2.0))/100.0)*TAX_MUT  # Very important!

DATA_RANGE = (-50, 51, 1)
FEATURES = np.arange(*DATA_RANGE)
Y_DATA = np.array(math_functions(FEATURES, 'square'))

IND = init_pop()  # Start population with random values in a range.

while 1:
    print('\n')
    print('AG Generation:', G, '\n')
    FIT = avaliation(IND, FEATURES, Y_DATA)
    crossover(IND, FIT)
    G = G+1
