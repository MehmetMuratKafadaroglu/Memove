import os
arr = os.listdir('C:\mapping\London Station Names')

i = 0
while i < len(arr):
    print("Old name", arr[i])
    old_name = 'C:\\mapping\\London Station Names\\' + arr[i]
    new_name ='C:\\mapping\\London Station Names\\' + arr[i].replace('↔', '-')
    if old_name != new_name:
        print("New name", new_name)
        os.rename(old_name, new_name)
    i = i + 1
