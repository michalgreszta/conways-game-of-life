# conways-game-of-life
A cellular automata written in Python as a university project

To start game, you have to set initial state of the cells. You can do that by clicking on the specific cells or by using prepared patterns.
The latter you can do pressing number key and then click on the board where you want to put your model.
In my cellular automata you can control transitions manually (S key) or automatically by pressing A, then you can change a speed of the transitions with the keys +/-.
By clicking A for the second time you stop automatic transitions.
You can add other patterns while automata is working!

General rules of transitions:
1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
2. Any live cell with two or three live neighbours lives on to the next generation.
3. Any live cell with more than three live neighbours dies, as if by overpopulation.
4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

Enjoy it!
