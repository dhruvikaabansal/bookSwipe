import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyDQ8JBRH4-Y95cFw3GkKY3v1jFMTxVF7V8",
    authDomain: "bookswipe-11d1f.firebaseapp.com",
    projectId: "bookswipe-11d1f",
    storageBucket: "bookswipe-11d1f.firebasestorage.app",
    messagingSenderId: "1071146499628",
    appId: "1:1071146499628:web:3346de98d07805ac095b89",
    measurementId: "G-NWQYN5TLB8"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

export { app, analytics, auth };
