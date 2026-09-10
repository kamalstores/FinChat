

export async function register({ username, password }: { username: string; password: string }) {
    try {
        const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/auth/register`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body: JSON.stringify({ username, password }),
            }
        );
        const data = await res.json();
        return data.access_token;
    } catch (err) {
        console.error("Register failed", err);
        throw err;
    }

};