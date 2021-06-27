$(function() {
    document.querySelector("#new-alert-rule").addEventListener('click', function(e) {
        document.querySelector('[data-role="add-alert-rule"]').innerText = 'Add New Rule';
        document.querySelector('#createalert').querySelector('form').reset();
        document.querySelector('#createalert').querySelector('form').action = '/alerts/';
        document.querySelector('#createalertLabel').innerHTML = 'Create Alert Rule';
        $('#createalert').modal()
    });

    document.querySelector('[name=project]').addEventListener('change', function(e) {
        // For the selected project, fetch possible aspect labels.
        el = e.target;
        projValue = el.value;
        fetch("/api/aspects-per-project/" + projValue + "/", { method: "GET" }).then(response => response.json()).then(data => {
            alertSelect = document.querySelector('[name=aspect]');
            options = alertSelect.querySelectorAll('option');
            for (var i = 0; i < options.length; i++) {
                let o = options[i];
                // First remove previous list.
                if (o.value != -1) {
                    o.remove();
                }
            }
            // Now add options for each possible aspect label for this project.
            for (var i = 0; i < data.length; i++) {
                console.debug(data[i]);
                let o = document.createElement('option');
                o.value = data[i];
                o.text = data[i];
                alertSelect.appendChild(o);
            }
        })
    });
    
    document.querySelectorAll('[data-role="delete-alert"]').forEach((e) => {
        e.addEventListener("click", (e) => {
            let alertId = e.currentTarget.getAttribute("data-alert-id")
            fetch("/alerts/" + alertId + "/", { method: "DELETE" }).then(response => {
                if (response.status == 200) {
                    location.reload()
                } else {
                    alert("Error deleting alert")
                }
            })
        })
    })

});

document.querySelectorAll('[data-role="edit-alert-button"]').forEach((element) => {
    element.addEventListener("click", (e) => {
        // Seed the modal form and then show it.
        let id = element.getAttribute("data-alert-id");
        url = "/alerts/" + id + "/"
        fetch(url).then(response => response.json()).then(data => {
            document.querySelector('[name=name]').value = data.name;
            document.querySelector('[name=emails]').value = data.emails;
            document.querySelector('[name=sms]').value = data.sms;
            document.querySelector('[name=keywords]').value = data.keywords;
            document.querySelector('[name=period]').value = data.period;
            document.querySelector('[name=frequency]').value = data.frequency;
            document.querySelector('[name=project]').value = data.project;

            var targetAspect = data.aspect;
            
            fetch("/api/aspects-per-project/" + data.project+ "/", {method: "GET"}).then(response => response.json()).then(data => {
                alertSelect = document.querySelector('[name=aspect]');
                options = alertSelect.querySelectorAll('option');
                for (var i = 0; i < options.length; i++) {
                    let o = options[i];
                    // First remove previous list.
                    if (o.value != -1) {
                        o.remove();
                    }
                }
                // Now add options for each possible aspect label for this project.
                for (var i = 0; i < data.length; i++) {
                    console.debug(data[i]);
                    let o = document.createElement('option');
                    o.value = data[i];
                    o.text = data[i];
                    alertSelect.appendChild(o);
                    if (o.value == targetAspect) {
                        o.selected = true;
                    }
                }
            })
        });
        
        $('#createalert').modal()
        
        // Change the button text and change the form action URL.
        document.querySelector('[data-role="add-alert-rule"]').innerText = 'Save Changes';
        document.querySelector('#createalert').querySelector('form').action= url;
        document.querySelector('#createalertLabel').innerHTML = 'Edit Alert Rule';
    })
})