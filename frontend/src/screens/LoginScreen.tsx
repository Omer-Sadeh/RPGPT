import React, {useState} from 'react';
import './LoginScreen.css';
import API from "../services/API";
import {BigButton} from "../components/Button";
import AUTH from "../services/auth";

function UserForm({title, onSubmit, modeChange, modeText}: {title: string, onSubmit: (username: string, password: string) => any, modeChange: () => void, modeText: string}) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [shake, setShake] = useState(false);

    const changeMode = () => {
        setError('');
        setUsername('');
        setPassword('');
        modeChange();
    }

    const handleSubmit = async () => {
        let err: string = await onSubmit(username, password);
        if (err) {
            setError(err);
            setShake(true);
            setTimeout(() => {
                setShake(false);
            }, 500);
        }
    }

    return (
        <div className="userForm">
            <div className="userSubTitle">{title}</div>
            <div className="userInput">
                <input type="text" value={username} placeholder="Username" onChange={(e) => setUsername(e.target.value)}/>
                <input type="password" value={password} placeholder="Password" onChange={(e) => setPassword(e.target.value)}/>
            </div>
            <div className={shake ? "userError shaking" : "userError"}>{error}</div>
            <BigButton text="Submit" func={handleSubmit} />
            <div className="userLink">{modeText} <a href="/#" onClick={changeMode}>Click here!</a></div>
        </div>
    );
}

function LoginScreen() {
    const [mode, setMode] = useState('login');
    const cookie = (name: "name" | "token", value: string) => {
        if (name === 'name') {
            AUTH.setName(value);
        } else {
            AUTH.setToken(value);
        }
    }

    const login = async (username: string, password: string) => {
        let err: string = '';
        let token = await API.login(username, password).catch((error) => {
            err = error.message;
        });
        if (token) {
            cookie('name', username);
            cookie('token', token);
        }
        return err;
    }

    const register = async (username: string, password: string) => {
        let err: string = '';
        let token = await API.register(username, password).catch((error) => {
            err = error.message;
        });
        if (token) {
            cookie('name', username);
            cookie('token', token);
        }
        return err;
    }

    const render = () => {
        switch (mode) {
            case 'login':
                return <UserForm title="Login" onSubmit={login} modeChange={() => setMode('register')}
                                 modeText="Dont have an account?"/>;
            case 'register':
                return <UserForm title="Sign Up" onSubmit={register} modeChange={() => setMode('login')}
                                    modeText="Already have an account?"/>;
            default:
                return <div/>;
        }
    }

    return (
        <div className="LoginPage">
            <div className="userTitle">
                <img src={process.env.PUBLIC_URL + '/Logo.png'} alt="logo"/>
            </div>
            {render()}
        </div>
    );
}

export default LoginScreen;