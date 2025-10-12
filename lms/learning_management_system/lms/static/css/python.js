document.addEventListener('DOMContentLoaded', () => {
    const topics = [
        { 
            title: "Module 1: Core Python Fundamentals", 
            items: [
                "Installation & Setup (IDE, VS Code)", 
                "Variables, Data Types (String, Int, Float, Bool)",
                "Operators & Conditional Statements (if, elif, else)",
                "Loops (for, while) & Control Flow",
                "Functions, Scope, and Lambda Expressions"
            ] 
        },
        { 
            title: "Module 2: Data Structures & OOP", 
            items: [
                "Lists, Tuples, Sets, and Dictionaries", 
                "File Handling (Reading and Writing)",
                "Error Handling & Exceptions (try, except, finally)",
                "Object-Oriented Programming (Classes, Objects, Inheritance)",
                "Modules, Packages, and the Standard Library"
            ] 
        },
        { 
            title: "Module 3: Data Science & Analysis (Libraries)", 
            items: [
                "NumPy for Numerical Computing", 
                "Pandas for Data Manipulation and Cleaning (DataFrames)",
                "Data Visualization with Matplotlib & Seaborn",
                "Introduction to Data Preprocessing",
                "Practical Data Analysis Project"
            ] 
        },
        { 
            title: "Module 4: Web Development & Automation", 
            items: [
                "Introduction to HTTP & APIs", 
                "Web Scraping with BeautifulSoup/Scrapy",
                "Building APIs with **Flask** (Lightweight Framework)",
                "Project: Creating a Simple Backend Web App",
                "Automation Scripts for System Tasks"
            ] 
        }
    ];

    const topicsContainer = document.querySelector('.topics-container');

    topics.forEach(module => {
        const card = document.createElement('div');
        card.className = 'topic-card';

        const title = document.createElement('h3');
        title.textContent = module.title;

        const ul = document.createElement('ul');
        module.items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            ul.appendChild(li);
        });

        card.appendChild(title);
        card.appendChild(ul);
        topicsContainer.appendChild(card);
    });

    // Optional: Add smooth scrolling for the "EXPLORE COURSE" button
    document.querySelector('.btn-primary').addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});