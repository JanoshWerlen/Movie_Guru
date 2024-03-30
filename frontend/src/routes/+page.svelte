<script>
    import { dev } from "$app/environment";
    let url = location.protocol + "//" + location.host;
    if (dev) {
        url = "http://localhost:5000";
    }

    let Runtime_in_Minutes = 0;
    let is_R_rated = 0;
    let is_english = 0;
    let tomato_score = 0;

    let predictedBoxOffice = "n.a.";
    let similar_movies = {};

    async function predict() {
        if (!validateInputs()) {
        return; // Stop the function if validation fails
    }
        let response = await fetch(
            `${url}/api/predict?` + new URLSearchParams({
                Runtime_in_Minutes,
                is_R_rated: is_R_rated ? 1 : 0,
                is_english: is_english ? 1 : 0,
                tomato_score
            }),
            {
                method: "GET",
            }
        );
        let data = await response.json();
        predictedBoxOffice = data.predicted_box_office;
        similar_movies = data.similar_movies;
    }
    function validateInputs() {
    if (Runtime_in_Minutes < 10 || Runtime_in_Minutes > 300) {
        alert('Runtime in Minutes must be between 10 and 300.');
        return false;
    }
    if (audience_score < 0 || audience_score > 100) {
        alert('Audience Score must be between 0 and 100.');
        return false;
    }
    if (tomato_score < 0 || tomato_score > 100) {
        alert('Tomato Score must be between 0 and 100.');
        return false;
    }
    return true;
    }

</script>
<style>
    body {
        height: 100%;
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f4;
        color: #333;
    }

    .container {
        background-color: white;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        max-width: 500px;
        text-align: center;
    }

    h1 {
        color: #007BFF;
        margin-bottom: 30px;
    }

    p {
        margin: 10px 0;
    }

    input[type="number"], input[type="checkbox"] {
        margin-left: 10px;
    }

    button {
        background-color: #007BFF;
        color: white;
        border: none;
        padding: 10px 15px;
        margin: 20px 0;
        cursor: pointer;
        border-radius: 5px;
    }

    button:hover {
        background-color: #0056b3;
    }

    table {
        margin-top: 20px;
        border-collapse: collapse;
        width: 100%;
    }

    td {
        padding: 8px 12px;
        border: 1px solid #ddd;
    }
</style>

<div class="container">
    <h1>Box_Office_Guru</h1>

    <p><strong>Runtime in Minutes</strong>
        <input type="number" bind:value={Runtime_in_Minutes} min="10" max="300" />
    </p>

    <p><strong>Is the Movie R rated (18+)?</strong>
        <input type="checkbox" bind:checked={is_R_rated} />
    </p>

    <p><strong>Original Language is English?</strong>
        <input type="checkbox" bind:checked={is_english} />
    </p>

    <p><strong>Tomatoscore?</strong>
        <input type="number" bind:value={tomato_score} min="0" max="100" />
    </p>

    <button on:click={predict}>Predict Box Office</button>

    <table>
        <tr>
            <td>Predicted Box Office:</td>
            <td>{predictedBoxOffice} Million</td>
        </tr>
        <tr>
            <td>Movies with a similar BoxOffice (+-5 Million):</td>
            <td>
                {#each similar_movies as movie}
                    <div>{movie}</div>
                {/each}
            </td>
        </tr>
    </table>
</div>
