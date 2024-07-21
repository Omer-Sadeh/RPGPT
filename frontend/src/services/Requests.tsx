import {toast} from "react-toastify";

const headers = {
    "Authorization": "Bearer TOKEN",
    "images": "True",
    'Content-Type': 'application/json'
};

export async function req(endpoint: string, auth: string = '', params: any = {}, data: any = {}) {
    let url = new URL(`${process.env.REACT_APP_BACKEND_URL}/${endpoint}`);
    let body: any = data;
    let header = headers;
    if (auth) {
        header["Authorization"] = "Bearer " + auth;
    }

    // If the value of a key in params is an object, add it to the body
    Object.keys(params).forEach(key => {
        if (typeof params[key] === 'object') {
            body[key] = params[key];
        } else{
            url.searchParams.append(key, params[key]);
        }
    });

    let request: any = {
        method: Object.keys(body).length > 0 ? 'POST' : 'GET',
        headers: header
    }
    if (Object.keys(body).length > 0) {
        request['body'] = JSON.stringify(body);
    }

    const response = await fetch(url, request).then(async (response) => {
        if (response.status !== 200) {
            let err = await response.json().then((data) => {
                return data.message;
            });
            return {status: "error", message: err};
        }
        let resultJSON = await response.json();
        return {status: "success", result: resultJSON};
    });

    if (response.status === "error") {
        toast.error("An error occurred! Please try again!", {
            position: "top-center",
            autoClose: 2000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: false,
            theme: "dark",
        });
        throw new Error(response.message);
    }
    return response.result;
}