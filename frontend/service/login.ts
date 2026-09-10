

export async function login(formData: URLSearchParams) {
    try {
        const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/x-www-form-urlencoded",
                },
                body: formData,
            }
        );

        const data = await res.json();
        return data.access_token;
    } catch (err) {
        console.error("Login failed", err);
        throw err;
    }

};