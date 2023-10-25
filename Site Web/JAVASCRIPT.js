document.addEventListener("DOMContentLoaded", function() {
    const gelData = {
        gel_used: 0,
        hands_detected: 0,
        date: new Date().toLocaleDateString(),
    };

    const gelDataHistory = [];

    const ctx = document.getElementById("usageChart").getContext("2d");

    const capaciteBouteille = 300;

    let usageChart;

    usageChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Gel utilisé (ml)",
                    backgroundColor: "blue",
                    data: [],
                },
                {
                    label: "Mains détectées",
                    backgroundColor: "red",
                    data: [],
                },
            ],
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                },
            },
        },
    });

    function updateChart() {
        usageChart.data.labels = gelDataHistory.map((data) => data.date);
        usageChart.data.datasets[0].data = gelDataHistory.map((data) => data.gel_used);
        usageChart.data.datasets[1].data = gelDataHistory.map((data) => data.hands_detected);
        usageChart.update();
    }

    function updateUsage(data) {
      const date = document.getElementById("date");
      date.textContent = `${data.date}`;
      const gelUsage = document.getElementById("gelUtilise");
      gelUsage.textContent = `${data.gel_used} ml`;
      const mainsDetectees = document.getElementById("mainsDetectees");
      mainsDetectees.textContent = `${data.hands_detected}`;
    }


    function updatePourcentage() {
        const pourcentageText = document.getElementById("pourcentage-text");
        const pourcentageRestant = ((capaciteBouteille - gelData.gel_used) / capaciteBouteille) * 100;
        pourcentageText.textContent = pourcentageRestant.toFixed(2) + "%";
    }

    function handleDataResponse(responseData) {
        if (responseData && typeof responseData === "object") {
            console.log("Données reçues du serveur :", responseData);
            const newData = {
                date: new Date().toLocaleDateString(),
                gel_used: responseData.gel_used || 0,
                hands_detected: responseData.hands_detected || 0,
            };

            gelDataHistory.push(newData);
            gelData.gel_used = newData.gel_used;
            gelData.hands_detected = newData.hands_detected;

            updateUsage(newData);
            updatePourcentage();
            updateChart();
            addToDataHistory(newData);
        } else {
            console.error("Données de réponse invalides.");
        }
    }

  function addToDataHistory(data) {
    const dataHistoryBody = document.getElementById("dataHistoryBody");

    const newRow = document.createElement("tr");
    const dateCell = document.createElement("td");
    dateCell.textContent = data.date;

    const gelUsedCell = document.createElement("tr");
    gelUsedCell.textContent = `${data.gel_used} ml`;

    const handsDetectedCell = document.createElement("td");
    handsDetectedCell.textContent = data.hands_detected;

    newRow.appendChild(dateCell);
    newRow.appendChild(gelUsedCell);
    newRow.appendChild(handsDetectedCell);

    dataHistoryBody.appendChild(newRow);
  }

    function fetchAndUpdateData() {
        const url = "https://serveur-flask.maxencelfrc.repl.co/obtenir_donnees_utilisation";     // CHANGER PAR L'URL DE VOTRE SERVEUR FLASK
        console.log("URL de la requête :", url);

        const xhr = new XMLHttpRequest();
        xhr.open("GET", url, true);

        xhr.onreadystatechange = function () {
            console.log("État de la requête :", xhr.readyState);
            if (xhr.readyState === 4) {
                console.log("Statut de la requête :", xhr.status);
                if (xhr.status === 200) {
                    const responseData = JSON.parse(xhr.responseText);
                    console.log("Réponse du serveur :", responseData);
                    handleDataResponse(responseData);
                } else {
                    console.error("Erreur");
                }
            }
        };
        xhr.send();
    }

    // Fonction pour mettre à jour les données
    function updateData() {
        fetchAndUpdateData();
    }

    // Mettre à jour les données automatiquement une fois par jour
    const updateInterval = 24 * 60 * 60 * 1000; // 24 heures en millisecondes
    setInterval(updateData, updateInterval);
    updateData(); // Appel initial pour mettre à jour immédiatement

    // Récupérez le bouton par son ID
    const updateButton = document.getElementById("updateButton");

    // Ajoutez un écouteur d'événements au bouton
    updateButton.addEventListener("click", function() {
        updateData(); // Appeler la fonction de mise à jour lors du clic sur le bouton
    });
});
