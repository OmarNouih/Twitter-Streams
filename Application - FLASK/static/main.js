document.addEventListener("DOMContentLoaded", function() {
    const wrapper = document.querySelector(".wrapper"),
        editableInput = wrapper.querySelector(".editable"),
        readonlyInput = wrapper.querySelector(".readonly"),
        placeholder = wrapper.querySelector(".placeholder"),
        counter = wrapper.querySelector(".counter"),
        button = wrapper.querySelector("button");

    editableInput.onfocus = () => {
        placeholder.style.color = "#c5ccd3";
    };
    editableInput.onblur = () => {
        placeholder.style.color = "#98a5b1";
    };

    editableInput.onkeyup = (e) => {
        let element = e.target;
        validated(element);
    };
    editableInput.onkeypress = (e) => {
        let element = e.target;
        validated(element);
        placeholder.style.display = "none";
    };

    function validated(element) {
        let text;
        let maxLength = 100;
        let currentlength = element.innerText.length;

        if (currentlength <= 0) {
            placeholder.style.display = "block";
            counter.style.display = "none";
            button.classList.remove("active");
        } else {
            placeholder.style.display = "none";
            counter.style.display = "block";
            button.classList.add("active");
        }

        counter.innerText = maxLength - currentlength;

        if (currentlength > maxLength) {
            let overText = element.innerText.substr(maxLength); // extracting over texts
            overText = `<span class="highlight">${overText}</span>`; // creating new span and passing over texts
            text = element.innerText.substr(0, maxLength) + overText; // passing overText value in textTag variable
            readonlyInput.style.zIndex = "1";
            counter.style.color = "#e0245e";
            button.classList.remove("active");
        } else {
            readonlyInput.style.zIndex = "-1";
            counter.style.color = "#333";
            text = element.innerText; // assigning current text if it's within the limit
        }
        readonlyInput.innerHTML = text; // replacing innerHTML of readonly div with textTag value
    }

	document.getElementById("tweetButton").addEventListener("click", function() {
		var tweetContent = document.querySelector(".readonly").innerText;
		console.log("Tweet Content:", tweetContent); // Log tweet content to debug
		
		var xhr = new XMLHttpRequest();
		xhr.open("POST", "/produce_tweets", true);
		xhr.setRequestHeader("Content-Type", "application/json");
		xhr.onreadystatechange = function() {
			if (xhr.readyState === 4) {
				console.log("AJAX Response:", xhr.responseText); 
				if (xhr.status === 200) {
					console.log("Tweets effacés avec succès !");
					document.querySelector(".editable").innerText = '';
					document.querySelector(".placeholder").style.display = "block";
					document.querySelector(".readonly").style.display = "none";
				} else {
					console.error("Erreur lors de la requête AJAX:", xhr.status); 
				}
			}
		};
		xhr.send(JSON.stringify({ tweetContent: tweetContent }));
	});
	
	
});
document.getElementById("streamCSVButton").disabled = false;

document.getElementById("streamCSVButton").addEventListener("click", function() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/stream_csv", true);
    let lastSuccessfulData = "";
    xhr.onprogress = function(event) {
        const receivedData = event.currentTarget.response.slice(lastSuccessfulData.length);
        const lines = receivedData.split('\n').filter(line => line.trim());

        lines.forEach(line => {
            try {
                const content = JSON.parse(line);
                document.querySelector(".editable").innerText = content.content; 
                document.querySelector(".readonly").innerText = content.content;  
                document.querySelector(".placeholder").style.display = "none"; 

                setTimeout(function() {
                    sendTweet(content.content);
                }, 3000);  // Adjusted from 2 to 3000 milliseconds for visibility

                lastSuccessfulData += line + "\n"; // Update last successful data received
            } catch (e) {
                console.log("Error parsing JSON:", e);
            }
        });
    };
    xhr.send();
});

function sendTweet(tweetContent) {
    console.log("Sending tweet:", tweetContent);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/produce_tweets", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            console.log("AJAX Response:", xhr.responseText);
            if (xhr.status === 200) {
                console.log("Tweet posted successfully!");
                document.querySelector(".editable").innerText = '';
                document.querySelector(".readonly").innerText = '';
                document.querySelector(".placeholder").style.display = "block";
            } else {
                console.error("Error during the AJAX request:", xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify({ tweetContent: tweetContent }));
}
