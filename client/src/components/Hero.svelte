<script>
    import SectionWrapper from "./SectionWrapper.svelte";
    import Header from "./Header.svelte";
    export let name;
    function loginWithToken(params) {
        let data = {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Imt5bGVnIiwiZW1haWwiOiJreWxlQGVtYWlsLmNvbSIsInBhc3N3b3JkIjoiZ0FBQUFBQm1jT2hPRDN1MDhqMjlCVDJUZVRfbHZiTkdscFhhNXBvbTFZYkwxWVVwRjVFTVBRZFRxb3ZnXy1CN3p0d1EybFFMN0VCeThIczhkMjFJVTZwTFdXd016TDJhbVE9PSIsImV4cCI6MTcxOTIwNjc3NH0.b_0J45OWZ7Qoy6BEwyCNo0RF-Qxomxvo8Ia9lx3EEc4"
        };
        let options = {
            method: "POST",
            mode: "no-cors", // no-cors, *cors, same-origin
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        };
        let url = "http://127.0.0.1:8000/api/v1/login/token";
        fetch(url, options).then(response => response.json()).then(data => console.log(data));
    }
</script>

<SectionWrapper>
    <Header />
    <div class="flex flex-col gap-10 flex-1 items-center justify-center pb-10 md:pb-14">
        <h2 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl max-w-[1200px] mx-auto w-full text-center">
            <span class="text-slate-600">Welcome, <span class="text-purple-700">{name!="" ? name:"Home"}</span>!</span>
        </h2>
    </div>
</SectionWrapper>