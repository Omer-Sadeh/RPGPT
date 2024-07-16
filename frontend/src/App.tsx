import React, {useEffect, useState} from 'react';
import API from './services/API';
import './App.css';
import MessageScreen, {LoadingScreen} from "./screens/MessageScreen";
import GameScreen from "./screens/GameScreen";
import LoginScreen from "./screens/LoginScreen";
import Screen from "./screens/Screen";
import AUTH from "./services/auth";

function App() {
    const [status, setStatus] = useState("loading");
    const [isMobile, setIsMobile] = useState(false);
    const [isLogged, setIsLogged] = useState(AUTH.check());

    useEffect(() => {
        window.addEventListener("resize", () => setIsMobile(window.innerWidth < 720))
        testStatus().then();
        // eslint-disable-next-line
    }, []);

    useEffect(() => {
        const interval = setInterval(() => {
            let status: boolean = AUTH.check();
            if (status !== isLogged) {
                setIsLogged(status);
            }
        }, 500);
        return () => clearInterval(interval);
    }, [isLogged]);

    const testStatus = async () => {
        if (!isMobile) {
            let status: boolean = await API.systemStatus().then((data) => {
                return data.length === 0;
            }).catch((error) => {
                console.log(error.message);
                return false;
            });
            setStatus(status ? "up" : "down");
        }
    }

    const renderScreen = () => {
        if (isMobile) return <MessageScreen message={"Not Supported!"}/>;
        return (<>
            <Screen isMounted={status === "loading"}><LoadingScreen/></Screen>
            <Screen isMounted={status === "down"}><MessageScreen message={"Server is down!"}/></Screen>
            <Screen isMounted={status === "up" && isLogged}><GameScreen /></Screen>
            <Screen isMounted={status === "up" && !isLogged}><LoginScreen/></Screen>
        </>);
    }

    return (
        <div className="App noselect">
            {renderScreen()}
        </div>
    );
}

export default App;
