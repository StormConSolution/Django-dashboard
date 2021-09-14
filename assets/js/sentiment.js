document.querySelector("#create-sentiment-button").addEventListener("click", (e)=>{
    $('#create-sentiment-modal').modal()
})

document.querySelectorAll("[data-role='delete-sentiment']").forEach((element) => {
    element.addEventListener("click", (e) => {
        let sentimentID = e.currentTarget.getAttribute("data-sentiment-id")
        fetch("/sentiment/" + sentimentID + "/", {
            method:'delete'
        }).then((response) => {
            if(response.status == 200){
                location.reload()
            } else {
				response.json().then(data => {
					alert(data.description)
				})
			}
        })
    })
})

document.querySelectorAll("[data-role='edit-sentiment-button']").forEach((element) => {
    element.addEventListener("click", (e) => {
        $("#edit-sentiment-modal").modal()
        
		let element = e.currentTarget
        let sentimentID = element.getAttribute("data-sentiment-id")
        let sentimentValue = element.getAttribute("data-sentiment-sentiment")
        let sentimentLanguage = element.getAttribute("data-sentiment-language")
        let sentimentText = element.getAttribute("data-sentiment-text")
        let sentimentLabel = element.getAttribute("data-sentiment-label")
		let apikey = element.getAttribute("data-sentiment-api-key")
        
		document.querySelector("#edit-sentiment-label").value = sentimentLabel
        document.querySelector("#edit-sentiment-text").value = sentimentText
        document.querySelector("#edit-sentiment-value").value = sentimentValue
        document.querySelector("#edit-sentiment-language").value = sentimentLanguage
        document.querySelector("#edit-sentiment-id").value = sentimentID
        document.querySelector("#edit-sentiment-rule-api-key-select").value = apikey
    })
})

document.querySelector("#create-sentiment-form").addEventListener("submit", (e)=>{
    e.preventDefault()
    let formData = new FormData(e.currentTarget)
    fetch("/sentiment/", {
        method: 'post',
        body: formData
    }).then(response => {
        if(response.status == 200){
            location.reload()
        } else {
            response.json().then(data => {
				alert(data.description)
            })
        }
    })
})

document.querySelector("#test-sentiment-form").addEventListener("submit", (e)=>{
    e.preventDefault()
    let formData = new FormData(e.currentTarget)
    let scoreDiv = document.querySelector("#test-sentiment-score")
    scoreDiv.innerHTML = "Loading..."
    fetch("/api/test-sentiment/", {
        method: 'post',
        body: formData
    }).then(response => {
        if(response.status == 200){
            response.json().then(data=>{
                scoreDiv.innerHTML = "Score: " + data.score
            })
        } else {
            scoreDiv.innerHTML = ""
            alert("Error testing sentiment")
        }
    })
})

document.querySelector("#edit-sentiment-form").addEventListener("submit", (e)=>{
    e.preventDefault()
    let formData = new FormData(e.currentTarget)
    let sentimentID = document.querySelector("#edit-sentiment-id").value
    fetch("/sentiment/" + sentimentID + "/", {
        method: 'post',
        body: formData
    }).then(response => {
        if(response.status == 200){
            location.reload()
        } else if(response.status == 400){
            response.text().then(data =>{
                alert("Error creating sentiment: " + data)
            })
        } else {
            alert("Error creating sentiment")
        }
    })
}) 
document.querySelector("#show-test-sentiment-modal").addEventListener("click", (e)=>{
    //document.querySelector("#test-sentiment-modal").style.display="block"
    $('#test-sentiment-modal').modal()
})
