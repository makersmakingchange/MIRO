# app
## Writing Tech For Jarrod
![alt text](https://github.com/WritingTechForJarrod/app/blob/master/img/readme.png?raw=true "wtfj")  
To run the app in console mode start the interpreter  
`python src/console.py`  

## Required functions
### Each piece must implement these functions
| message type | piece name | | args |
|:---|:---:|:---:|:---:|
| incoming | @piece_name | stop | |
| incoming | @piece_name | marco | |
### Each piece must emit these messages
|:---|:---:|:---:|:---:|
| outgoing | started | piece_name | |
| outgoing | stopping | piece_name | | 
### Messages must have the format
|:---|:---:|:---:|:---:|
| incoming | @piece_name | function | data |
| outgoing | piece_name | topic | data |
Space is used as a delimiter between the first three items  
  
The console has the following special commands:
`start piece_name` 
`start all`
`restart piece_name`  
`restart all`  
`stop piece_name` 
`stop all`  
`quit`  
`quit!` - _stop all pieces and quit_