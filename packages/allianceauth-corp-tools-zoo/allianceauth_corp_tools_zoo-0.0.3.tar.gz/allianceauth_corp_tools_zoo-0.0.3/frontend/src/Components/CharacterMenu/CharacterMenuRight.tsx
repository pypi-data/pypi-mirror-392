import styles from "./CharMenu.module.css";
import React from "react";
import { Nav } from "react-bootstrap";
import ReactDOM from "react-dom";
import { useTranslation } from "react-i18next";
import { useIsFetching } from "react-query";
import { MenuItem } from "./MenuParts";

const menuRoot = document.getElementById("nav-right");

const CharMenuRight = () => {
  const { t } = useTranslation();

  const isLoading = useIsFetching();

  React.useEffect(() => {
    if (menuRoot) {
      // Clear existing content safely by removing children one at a time
      while (menuRoot.firstChild) {
        menuRoot.removeChild(menuRoot.firstChild);
      }
    }
  }, []);

  const menuListLink = {
    link: "account/list",
    name: t("Account List"),
  };

  if (!menuRoot) {
    return <></>;
  }
  return ReactDOM.createPortal(
    <>
      {isLoading ? (
        <>
          <Nav.Link>
            <i className={`fas fa-sync-alt fa-fw ${styles.menuRefreshSpin}`} />
          </Nav.Link>
        </>
      ) : (
        <></>
      )}
      <Nav.Item as="li">
        <Nav.Link href="/audit/char/add/" key="Add Character">
          {t("Add Character")}
        </Nav.Link>
      </Nav.Item>
      <MenuItem link={menuListLink} />
      {/* TODO Check perms for this */}
      {/* <Nav.Item as="li">
        <Nav.Link as={Link} to={`/audit/r_beta/corp`} key="corp-swap">
          <i className="fa-regular fa-building"></i>
        </Nav.Link>
      </Nav.Item> */}
    </>,
    menuRoot,
  );
};

export { CharMenuRight };
