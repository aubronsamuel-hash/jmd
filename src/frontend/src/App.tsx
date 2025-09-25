import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/layout/app-layout";
import { MissionTemplatesPage } from "./pages/mission-templates/mission-templates-page";
import { ProjectDetailPage } from "./pages/projects/project-detail-page";
import { ProjectsListPage } from "./pages/projects/projects-list-page";
import { SessionProvider } from "./providers/session-provider";
import { queryClient } from "./providers/tanstack";

function App(): JSX.Element {
  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Navigate to="/projects" replace />} />
            <Route path="/projects" element={<ProjectsListPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="/mission-templates" element={<MissionTemplatesPage />} />
          </Routes>
        </AppLayout>
        <ReactQueryDevtools initialIsOpen={false} position="bottom-right" />
      </QueryClientProvider>
    </SessionProvider>
  );
}

export default App;
