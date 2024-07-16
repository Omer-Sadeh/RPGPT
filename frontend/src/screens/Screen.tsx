import "./Screen.css";
import FadeScreen from "../components/FadeScreen";

function Screen({ children, isMounted } : { children: any, isMounted: boolean }) {
    return <FadeScreen show={isMounted} classname="screen">{children}</FadeScreen>;
}

export default Screen;