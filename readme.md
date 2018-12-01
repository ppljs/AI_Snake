# Snake AI :snake:

An evolutionary algorithm that ajusts the weights of a neural network to control a snake. 

<p align="center">
  <a href="Snake AI">
    <img src="https://github.com/PauloLemgruberJeunon/AI_Snake/blob/master/snake_ai.gif?raw=true" />
  </a>
</p>

## Prerequisites

* Kivy  
  * See instalation instrutions https://kivy.org

* Install pip dependencies  
  * ```pip install -r requirements.txt```

## Running the program
```
python src/main.py
```

* In the file main.py at lines 123, 124 and 125 we have the variables USE_GUI, USE_SAVE and MANUAL. 
  * USE_GUI enable the visual interface.
  * USE_SAVE makes the program use the file save.pkl as the Snake AI
  * MANUAL let you play the game! :smile:

## AI Learning  
  <img src="nn.png" align="center" width="520">

* 1° Start #population_size individuals of neural network with random weights.  
* 2° The population of neural networks are evaluated and ranked by their fitness.
  * The fitness of each neural network is calculated by analysing the movements of the snake.
      * Eat an apple, fitness += 40  
      * Move farther the apple, fitness -= 3  
      * Move closer the appple, fitness += 1  
  * It's important to give a high value for eating the apple because sometimes the snake needs to make a distant path to reach the apple and that will compensate the negatives values given by moving father.  
  * Moving father needs to be higher in module than moving close to make the snake stop running in circle.

* 3° Remove some percentage of the population worst individuals and add new ones.
  * It's important to recreate some indivuals because sometimes to reach a higher fitness it's needed to make a bigger change in the weights which it's not achievable using crossover and mutations (maximum local).

* 4° Make the crossover.
* 5° Make the mutation.
* 6° Start a new generation.

* Observation: One of the evalution problems is the noise given by the location of the apples. Sometimes the apple can be in better place and this may give a higher fitness incorrectly. To reduce this noise and improve the fitness acurracy, it's important to evaluate the same network more than one time (play more games).

