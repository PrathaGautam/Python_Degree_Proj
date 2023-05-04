// const form = document.getElementById("signup-form");
// const response = document.getElementById("response");
//
// form.addEventListener("Sign up", (event) =>
// {
//     event.preventDefault();
//
//     // Get form data
//     const name = form.name.value.trim();
//     const email = form.email.value.trim();
//     const password = form.password.value.trim();
//     const passwordRepeat = form["password-repeat"].value.trim();
//    console.log("Name: " + name);
//    console.log("Email: " + email);
//    console.log("Password: " + password);
//    console.log("Password repeat : " + passwordRepeat);
//
//     // Validate form data
//     if (name === "") {
//         alert("Please enter your name.");
//         //return;
//     }
//
//     if (email === "") {
//         alert("Please enter your email.");
//         //return;
//     }
//
//     if (!isValidEmail(email)) {
//         alert("Please enter a valid email address.");
//         //return;
//     }
//
//     if (password === "") {
//         alert("Please enter a password.");
//         //return;
//     }
//
//     if (password !== passwordRepeat) {
//         alert("Passwords do not match.");
//         //return;
//     }
//
//     // Submit form data
//     const data = {
//         name,
//         email,
//         password,
//     };
//     fetch("http://localhost:8000/signup", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//         },
//         body: JSON.stringify(data),
//     })
//         .then(response => response.json())
//         .then(json => {
//             if (json.success) {
//                 // Redirect to success page
//                 window.location.href = "Success_sign_in.html";
//             } else {
//                 // Display error message
//                 alert(json.message);
//             }
//         })
//         .catch(error => {
//             console.error(error);
//         });
// });
//
// function isValidEmail(email) {
//     // Simple email validation regex
//     const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
//     return regex.test(email);
// }

