# app
## Writing Tech For Jarrod
![alt text](https://github.com/WritingTechForJarrod/app/blob/master/img/readme.png?raw=true "wtfj")  
To run the app in console mode start the interpreter  
`python src/console.py`  

## Message format
### Each piece must execute these functions upon receiving these messages
| id | function |
|:---|:---:|
| @piece_name | stop |
| @piece_name | marco | -- respond with `piece_name polo` 
### Each piece must emit these messages upon startup and exit
| message | id |
|:---|:---:|:---:|
| started | piece_name | |
| stopping | piece_name | | 
### Other messages must have the format
| message type | piece name | description | |
|:---|:---:|:---:|:---:|
| _incoming_ | @piece_name | function | data |
| _outgoing_ | piece_name | topic | data |
Space is used as a delimiter between the sections of each message
  
The console has the following special commands:
`start piece_name`  
`start all`  
`restart piece_name`  
`restart all`  
`stop piece_name`  
`stop all`  
`quit`  
`quit!` - _stop all pieces and quit_