<script>
    import { onMount } from "svelte";
    import Hero from "../components/Hero.svelte"

    onMount(async() => {
        let url = "http://127.0.0.1:8000/api/v1/login/token";
        let options = {
            method: "POST",
            mode: "no-cors",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Imt5bGVnIiwiZW1haWwiOiJreWxlQGVtYWlsLmNvbSIsInBhc3N3b3JkIjoiZ0FBQUFBQm1lTlN2ckhNVWxOcnRvZzhGblFkVHlMaHpjR2JZbVUtb0w5cFVwOE1CcVA2WlFfcnMzbU5IaFI5LUVOUFA3UlFTRm1oTF9fUHFWS0QzZHNMRWV4aU1rU1NZNkE9PSIsImV4cCI6MTcxOTM2NzU5OX0.kNTwLm_h7Ek2chVQdzbmJoTN5fkok-Ft3LoJruWRZ4Q"
            })
        }
        let response = await fetch(url, options);
        let data = await response.text();
    })
</script>

<main class="flex flex-col bgGrid">
    <Hero name=""/>
</main>