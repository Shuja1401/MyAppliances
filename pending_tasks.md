How to introduce * in the password field? Also, learn how password works.
Welcome page should also take you to HOME. Right now, it takes you only to login.
Welcome page url is still /onboarding. Why??
If unique constraints are not unique, it should handle it gracefully.
Validation checks. ALL Possibilities.
  - Date should be withing a range, in correct format. Suggest the format. If not in correct format, it should prompt.
  - Phone number. Add an option to enter ISD codes. Also perform a validation for phone number. 10 digits.
MAIN MENU >> ENTER THE DETAILS OF THE SERVICE IS MISSING.
**On each page, it should show at the top: username, Logout, Home**
In the device_details form, add a line informing user that extended warranty field is applicable, only if the answer to the above question is "YES". Make it optional, if the above response is NO.
From device_details form, remove "add device" option. Use the Header: username, Logout, Home.
Change navigation to hyperlinks, instead of option entry.
Add an exit page. Display message - "Thanks for using MyAppliances. Visit again!" Add hyperlinks to create account and login.
Remove debug checks from add_device route.
In add_device, remove option of Home. It should take you to navigation.
Make this option if previous option (no service plan) is NO ->>Is the plan by manufacturer or a third-party?

After adding device, it should take you to a new page: device added successfully, do you want to:

Add another device
Main menu
Logout




Pending things
Add option to add/view/delete service details as well.
3. Service details
   3.1 Add
   3.2 View
   3.3 delete

service due
warranty due


service_warranty_status_check: add service_status_check and warranty_status_check columns


Can we connect it to another app of service provider? 


