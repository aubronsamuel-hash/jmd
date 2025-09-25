import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { useCreateProject, useProjects } from "@/features/projects/hooks";
import { useVenues } from "@/features/venues/hooks";
import type { ProjectCreate } from "@/lib/api/types";

const initialFormState: ProjectCreate = {
  name: "",
  description: "",
  startDate: "",
  endDate: "",
  budgetCents: undefined,
  teamType: "",
  venueIds: [],
};

export function ProjectsListPage(): JSX.Element {
  const { data: projects, isLoading, isError, error } = useProjects();
  const { data: venues } = useVenues();
  const createProject = useCreateProject();
  const [formState, setFormState] = useState<ProjectCreate>(initialFormState);

  const sortedProjects = useMemo(() => {
    return (projects ?? []).slice().sort((a, b) => a.name.localeCompare(b.name));
  }, [projects]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!formState.name.trim()) {
      return;
    }
    try {
      await createProject.mutateAsync({
        ...formState,
        budgetCents: formState.budgetCents ? Number(formState.budgetCents) : undefined,
        venueIds: formState.venueIds,
      });
    } catch (error) {
      // L'erreur est gérée par React Query (états isError / error).
    } finally {
      setFormState(initialFormState);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-2xl">Projets</CardTitle>
          <CardDescription>
            Visualisez vos projets actifs, accédez aux fiches détaillées et surveillez les budgets.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col gap-4" aria-busy>
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : isError ? (
            <div
              role="alert"
              className="rounded-md border border-destructive bg-destructive/10 p-4 text-sm"
            >
              Impossible de charger les projets :{" "}
              {error instanceof Error ? error.message : "erreur inconnue"}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>Période</TableHead>
                    <TableHead>Budget</TableHead>
                    <TableHead>Type d&apos;équipe</TableHead>
                    <TableHead>Salles</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedProjects.map((project) => (
                    <TableRow key={project.id} className="hover:bg-accent/30">
                      <TableCell>
                        <Link to={`/projects/${project.id}`} className="font-medium text-primary">
                          {project.name}
                        </Link>
                        {project.description ? (
                          <p className="text-xs text-muted-foreground">{project.description}</p>
                        ) : null}
                      </TableCell>
                      <TableCell>
                        {project.startDate ? (
                          <span>
                            {new Date(project.startDate).toLocaleDateString()} —{" "}
                            {project.endDate ? new Date(project.endDate).toLocaleDateString() : "?"}
                          </span>
                        ) : (
                          <span className="text-muted-foreground">Non planifié</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {typeof project.budgetCents === "number"
                          ? new Intl.NumberFormat("fr-FR", {
                              style: "currency",
                              currency: "EUR",
                            }).format(project.budgetCents / 100)
                          : "—"}
                      </TableCell>
                      <TableCell>{project.teamType ?? "—"}</TableCell>
                      <TableCell className="space-y-1">
                        {project.venues.length > 0 ? (
                          project.venues.map((venue) => (
                            <Badge key={venue.id} variant="secondary">
                              {venue.name}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-muted-foreground">Aucune salle</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {sortedProjects.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        Aucun projet enregistré pour le moment.
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card aria-live="polite">
        <CardHeader>
          <CardTitle>Créer un projet</CardTitle>
          <CardDescription>
            Renseignez les informations clés pour démarrer la planification d&apos;un nouvel
            événement.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="project-name">Nom du projet</Label>
              <Input
                id="project-name"
                required
                value={formState.name}
                onChange={(event) =>
                  setFormState((state) => ({ ...state, name: event.target.value }))
                }
                placeholder="Festival d'été"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="project-description">Description</Label>
              <Textarea
                id="project-description"
                value={formState.description ?? ""}
                onChange={(event) =>
                  setFormState((state) => ({ ...state, description: event.target.value }))
                }
                placeholder="Détails de l'événement, contraintes, etc."
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="project-start">Début</Label>
                <Input
                  id="project-start"
                  type="date"
                  value={formState.startDate ?? ""}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, startDate: event.target.value }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-end">Fin</Label>
                <Input
                  id="project-end"
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
                <Label htmlFor="project-budget">Budget (€)</Label>
                <Input
                  id="project-budget"
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
                <Label htmlFor="project-team">Type d&apos;équipe</Label>
                <Input
                  id="project-team"
                  value={formState.teamType ?? ""}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, teamType: event.target.value }))
                  }
                  placeholder="Technique, artistique, mixte..."
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="project-venues">Salles associées</Label>
              <select
                id="project-venues"
                multiple
                className="h-32 w-full rounded-md border border-input bg-background p-3 text-sm"
                value={formState.venueIds}
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
              <p className="text-xs text-muted-foreground">
                Maintenez Ctrl (Windows) ou Cmd (macOS) pour sélectionner plusieurs salles.
              </p>
            </div>
            <Button type="submit" className="w-full" disabled={createProject.isPending}>
              {createProject.isPending ? "Création en cours..." : "Créer"}
            </Button>
            {createProject.isError ? (
              <p role="alert" className="text-sm text-destructive">
                Impossible d&apos;enregistrer le projet :{" "}
                {createProject.error instanceof Error
                  ? createProject.error.message
                  : "erreur inconnue"}
              </p>
            ) : null}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
