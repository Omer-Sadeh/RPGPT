class AUTH {

    static check() : boolean {
        return localStorage.getItem('token') !== null;
    }

    static setName(name: string) {
        localStorage.setItem('name', name);
    }

    static setToken(token: string) {
        localStorage.setItem('token', token);
    }

    static getName() : string {
        return localStorage.getItem('name') as string;
    }

    static getToken() :  string {
        return localStorage.getItem('token') as string;
    }

    static ResetAuth() {
        localStorage.removeItem('name');
        localStorage.removeItem('token');
    }
}

export default AUTH;