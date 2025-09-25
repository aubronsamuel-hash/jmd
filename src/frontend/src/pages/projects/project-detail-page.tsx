import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useDeleteProject, useProject, useUpdateProject } from "@/features/projects/hooks";
import { useVenues } from "@/features/venues/hooks";
import type { ProjectUpdate } from "@/lib/api/types";

const emptyUpdate: ProjectUpdate = {
  name: "",
  description: "",
  startDate: "",
  endDate: "",
  budgetCents: undefined,
  teamType: "",
  venueIds: [],
};

export function ProjectDetailPage(): JSX.Element {
  const params = useParams();
  const projectId = params.projectId ?? "";
  const navigate = useNavigate();
  const { data: project, isLoading, isError, error } = useProject(projectId);
  const { data: venues } = useVenues();
  const updateProject = useUpdateProject(projectId);
  const deleteProject = useDeleteProject(projectId);
  const [formState, setFormState] = useState<ProjectUpdate>(emptyUpdate);

  useEffect(() => {
    if (project) {
      setFormState({
        name: project.name,
        description: project.description ?? "",
        startDate: project.startDate ?? "",
        endDate: project.endDate ?? "",
        budgetCents: project.budgetCents,
        teamType: project.teamType ?? "",
        venueIds: project.venues.map((venue) => venue.id),
      });
    }
  }, [project]);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!project) {
      return;
    }
    updateProject.mutate({
      ...formState,
    });
  };

  const handleDelete = () => {
    if (!project) {
      return;
    }
    if (window.confirm("Confirmez-vous la suppression du projet ?")) {
      deleteProject.mutate(undefined, {
        onSuccess: () => navigate("/projects"),
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Chargement du projet</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-40 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (isError || !project) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Projet introuvable</CardTitle>
          <CardDescription>
            {error instanceof Error
              ? error.message
              : "Impossible de charger les informations du projet."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={() => navigate(-1)}>
            Retour
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card>
        <CardHeader>
          <CardTitle>{project.name}</CardTitle>
          <CardDescription>Mettre à jour les informations projet.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="project-name-detail">Nom</Label>
              <Input
                id="project-name-detail"
                value={formState.name ?? ""}
                onChange={(event) =>
                  setFormState((state) => ({ ...state, name: event.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="project-description-detail">Description</Label>
              <Textarea
                id="project-description-detail"
                value={formState.description ?? ""}
                onChange={(event) =>
                  setFormState((state) => ({ ...state, description: event.target.value }))
                }
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="project-start-detail">Début</Label>
                <Input
                  id="project-start-detail"
                  type="date"
                  value={formState.startDate ?? ""}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, startDate: event.target.value }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-end-detail">Fin</Label>
                <Input
                  id="project-end-detail"
                  type="date"
                  value={formState.endDate ?? ""}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, endDate: event.target.value }))
                  }
                />
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="project-budget-detail">Budget (€)</Label>
                <Input
                  id="project-budget-detail"
                  type="number"
                  min={0}
                  step={100}
                  value={formState.budgetCents ? String(formState.budgetCents / 100) : ""}
                  onChange={(event) =>
                    setFormState((state) => ({
                      ...state,
                      budgetCents: event.target.value
                        ? Number(event.target.value) * 100
                        : undefined,
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-team-detail">Type d&apos;équipe</Label>
                <Input
                  id="project-team-detail"
                  value={formState.teamType ?? ""}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, teamType: event.target.value }))
                  }
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="project-venues-detail">Salles</Label>
              <select
                id="project-venues-detail"
                multiple
                className="h-32 w-full rounded-md border border-input bg-background p-3 text-sm"
                value={formState.venueIds ?? []}
                onChange={(event) => {
                  const options = Array.from(event.target.selectedOptions).map(
                    (option) => option.value,
                  );
                  setFormState((state) => ({ ...state, venueIds: options }));
                }}
              >
                {(venues ?? []).map((venue) => (
                  <option key={venue.id} value={venue.id}>
                    {venue.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-end">
              <Button type="submit" disabled={updateProject.isPending}>
                {updateProject.isPending ? "Enregistrement..." : "Enregistrer"}
              </Button>
              <Button
                type="button"
                variant="destructive"
                onClick={handleDelete}
                disabled={deleteProject.isPending}
              >
                Supprimer
              </Button>
            </div>
            {updateProject.isError ? (
              <p role="alert" className="text-sm text-destructive">
                Erreur lors de la mise à jour :{" "}
                {updateProject.error instanceof Error
                  ? updateProject.error.message
                  : "erreur inconnue"}
              </p>
            ) : null}
            {updateProject.isSuccess ? (
              <p role="status" className="text-sm text-emerald-600">
                Projet mis à jour avec succès.
              </p>
            ) : null}
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Résumé</CardTitle>
          <CardDescription>Mises à jour récentes et lieux associés.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <h3 className="text-xs uppercase text-muted-foreground">Identifiant</h3>
            <p className="font-mono text-xs">{project.id}</p>
          </div>
          <div>
            <h3 className="text-xs uppercase text-muted-foreground">Mise à jour</h3>
            <p>{new Date(project.updatedAt).toLocaleString()}</p>
          </div>
          <div>
            <h3 className="text-xs uppercase text-muted-foreground">Salles</h3>
            <div className="flex flex-wrap gap-2">
              {project.venues.length ? (
                project.venues.map((venue) => (
                  <Badge key={venue.id} variant="secondary">
                    {venue.name}
                  </Badge>
                ))
              ) : (
                <span className="text-muted-foreground">Aucune salle associée</span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
