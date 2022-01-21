# Computational Intelligence 2021-2022

Computational Intelligence exam done by Samuel Oreste Abreu - s281568

# Description

This here developed software consists of a fully working Hanabi agent, the main implementation is that of an optimized agent
through Genetic Algorithm using a floating point representation.

## Agent

The agents are instantiated through the file player.py.

Arguments: 

+ num_players: Number of agents that are going to be instantiated (Default: 1)
+ log: Level in which the log is going to output to console (Default: info)
+ iterations: Amount of games to play (Default: 1)
+ training: Training mode
+ player_type: Type of agent that is going to be instantiated (Only one is actually instantiated, the others are deterministic agents)
+ slowmode: Slows the execution, recommended for games with less than 3 players

Arguments for agent of type GA
+ ga_max_playability: Set the max_playability (Default 0.6) (Higher means more likely to maximize the playability)
+ random_discard: Set the random discard (Default: 0.5) (>0.5 means random discard)
+ random_hint: Set the random hint (Default: 0.5) (>0.5 means random hint)

Example for playing with itself:
```
python player.py --num_players [1|2|3|4|5] --player_type [ga|deterministic|random]
```

## GA agent

Set-up in which the GA agent learns what the best chromosome is by playing with itself.

Arguments: 

+ num_players: Number of agents that are going to be instantiated (Default: 1)
+ log: Level in which the log is going to output to console (Default: info)
+ iterations: Amount of games to play (Default: 1)
+ training: Training mode
+ player_type: Type of agent that is going to be instantiated (Only one is actually instantiated, the others are deterministic agents)

Arguments for agent of type GA
+ ga_max_playability: Set the max_playability (Default 0.6) (Higher means more likely to maximize the playability)
+ random_discard: Set the random discard (Default: 0.5) (1.0 means random discard)
+ random_hint: Set the random hint (Default: 0.5) (1.0 means random hint)

## Extra comments and observations

+ It was implemented using threads in order to further simulate turns through the usage of barriers, however, this didn't help.
+ Python would point to the wrong 'self' object whenever a thread was instantiated outside of the module file (Reasons unknown).
+ After many iterations it was observed that in games with many players a player which has some idea of how to play would not affect the final result much.
+ On the other hand, a player can indeed negatively influence the game (Due to either ignorance or maliciousness) and ruin the match.
+ A ga_max_playability of between 0.6 and 0.8 was considered to be optimal.
+ random_discard seemingly had no effect on the final score.
+ random_hint is preferred to be <0.5.

## Possible improvements

+ Addition of further playing rules.

+ Numbering of turns in the server-side application would greatly simplify this code.
+ Decreasing the size of fixed packets or using variable length packets (As sometimes the server's packet buffer would fill way too fast)

## Original comments

Exam of computational intelligence 2021 - 2022. It requires teaching the client to play the game of Hanabi (rules can be found [here](https://www.spillehulen.dk/media/102616/hanabi-card-game-rules.pdf)).

## Server

The server accepts passing objects provided in GameData.py back and forth to the clients.
Each object has a ```serialize()``` and a ```deserialize(data: str)``` method that must be used to pass the data between server and client.

Watch out! I'd suggest to keep everything in the same folder, since serialization looks dependent on the import path (thanks Paolo Rabino for letting me know).

Server closes when no client is connected.

To start the server:

```bash
python server.py <minNumPlayers>
```

Arguments:

+ minNumPlayers, __optional__: game does not start until a minimum number of player has been reached. Default = 2


Commands for server:

+ exit: exit from the server

## Client

To start the server:

```bash
python client.py <IP> <port> <PlayerName>
```

Arguments:

+ IP: IP address of the server (for localhost: 127.0.0.1)
+ port: server TCP port (default: 1024)
+ PlayerName: the name of the player

Commands for client:

+ exit: exit from the game
+ ready: set your status to ready (lobby only)
+ show: show cards
+ hint \<type> \<destinatary>:
  + type: 'color' or 'value'
  + destinatary: name of the person you want to ask the hint to
+ discard \<num>: discard the card *num* (\[0-4]) from your hand
