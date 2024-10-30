# Cpnits Check11

Check11 checks Python >= 3.10 code for cpnits.com students
How to use:

## How to use check11: 
	check11 /absolute/path/to/dir/with/assignment/ 
or 
	check11 relative/path/with/assignment/ 
	
or in current working directory: 
	check11 -c 

## For help: 
	check11 -h 
	
## Additional arguments
Additional arg for no traceback:  
	check11 --t /some/dir 
	
Additional arg for errors only:  
	check11 --e /some/dir 
	
Additional arg for clearing prompt:
	check11 --p /some/dir 
	
Combined args for no traceback and errors only: 
	check11 --et /some/dir 

## Examples
Example (assignment in current dir, errors only, no traceback, clear prompt): 
	check11 --etp -c
Example (assignment in relative dir assignment, clear prompt): 
	check11 --p assignment/

[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)