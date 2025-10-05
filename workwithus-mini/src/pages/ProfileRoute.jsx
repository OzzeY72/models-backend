import { useParams } from "react-router-dom";
import ProfilePage from "./ProfilePage";

export default function ProfileRoute() {
  const { id } = useParams();
  return <ProfilePage id={id} />;
}
