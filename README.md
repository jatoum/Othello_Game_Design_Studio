# Othello_Game_Design_Studio
CS 6388 Model-Integrated Computing final project.

## Introduction
Discover the Othello Game Studio, an extensive design platform crafted for both creating and engaging in the Othello (Reversi) game. This studio encompasses a visualizer, game logic plugins, and a meta-model, promising an immersive gaming venture

## Installation Instructions

### Prerequisites
1. EnsurePython3 (version 3.11.0 or higher, if applicable)
2. Ensure Node.js (version 20.9.0 LTS or higher)

### Steps 
1. Clone the repository and navigate to the directory
```
git clone https://github.com/jatoum/Othello_Game_Design_Studio.git
cd [repository directory/myminiproject]
```
2. Install dependencies
```
npm install
```
3. Download/Install Docker Desktop from this link.
4. Download/Install the latest version of mongo in Docker Image.
5. Create a mongo image. Optionally, set the Host path as
```
[repository directory]/DB
```
and set the Container path as
```
/data/db
```
6. Open a new terminal and plugin the following command.
```
node app.js
```
7. Open a new browser tab and enter [http://localhost:8888] to navigate to the web address.

## Implementation Overview

### Structure
** src/: Home to the studio's source code.
** plugins/: Game logic plugins (Highlight valid tiles, Counting pieces, Flipping, Undo).
** visualizers/: Components for Othello game visualization.
** meta/: Meta-model defining the game.

## Technologies Employed
1. We used React.js for front-end visualization.
2. We used Node.js for back-end services.
3. We used WebGME for model integration.
4. We used Python for the plugins.

## How to run the game

### Playing the Game
1. Start a New Game:
 ```
 Initiate a new Othello board by clicking 'New Game'.
3. Making Moves:
```
  Place your piece by clicking on a valid tile.
  Valid tiles are highlighted based on the current game state.
```
4. Game Progression:
```
Automatic counting and display of the number of pieces for each color.
Board updates after each move to reflect the new state.
```
5. End of the Game
```
The game concludes when no valid moves are available.
Display of the final score indicates the winner.

### End of the Game
* The game concludes when no valid moves are available.
* Display of the final score indicates the winner.

## Repository Contents
* README.md: Documentation file.
* src/: Source code directory.

## Deployment
The installation instructions appended above can be used to deploy the Othello Game Studio on your local machine.
