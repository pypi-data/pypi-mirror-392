"""
R Workspace Bridge - Access RStudio Console Objects
===================================================

Allows cite-agent to read datasets and objects from RStudio's workspace
that haven't been saved to disk yet.

Solves the problem: "I imported data in R but can't access it from the agent"
"""

import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd


class RWorkspaceBridge:
    """Bridge to access R workspace objects without saving to disk"""

    def __init__(self, r_executable: str = "Rscript"):
        self.r_executable = r_executable
        self.temp_dir = Path(tempfile.gettempdir()) / "r_workspace_bridge"
        self.temp_dir.mkdir(exist_ok=True)

    def list_objects(self, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        List all objects in R workspace

        Args:
            workspace_path: Path to .RData file (optional, uses current session if None)

        Returns:
            Dict with object names, types, dimensions
        """
        r_code = """
        # Load workspace if specified
        workspace_file <- commandArgs(trailingOnly = TRUE)[1]
        if (!is.na(workspace_file) && file.exists(workspace_file)) {
            load(workspace_file)
        }

        # Get all objects
        obj_names <- ls()

        # Build info for each object
        obj_info <- lapply(obj_names, function(name) {
            obj <- get(name)
            list(
                name = name,
                class = class(obj)[1],
                type = typeof(obj),
                size = as.numeric(object.size(obj)),
                dimensions = if(is.null(dim(obj))) length(obj) else paste(dim(obj), collapse="x"),
                is_dataframe = is.data.frame(obj),
                is_matrix = is.matrix(obj),
                is_vector = is.vector(obj),
                preview = if(is.data.frame(obj)) {
                    paste(colnames(obj), collapse=", ")
                } else if(is.vector(obj) && length(obj) <= 5) {
                    paste(head(obj, 5), collapse=", ")
                } else {
                    ""
                }
            )
        })

        # Convert to JSON
        cat(jsonlite::toJSON(obj_info, auto_unbox = TRUE))
        """

        try:
            # Write R code to temp file
            r_script = self.temp_dir / "list_objects.R"
            r_script.write_text(r_code)

            # Run R script
            cmd = [self.r_executable, str(r_script)]
            if workspace_path:
                cmd.append(workspace_path)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                objects = json.loads(result.stdout)
                return {
                    "success": True,
                    "objects": objects,
                    "count": len(objects)
                }
            else:
                return {
                    "error": f"R execution failed: {result.stderr}",
                    "success": False
                }

        except subprocess.TimeoutExpired:
            return {"error": "R script timed out after 30 seconds", "success": False}
        except Exception as e:
            return {"error": f"Failed to list R objects: {str(e)}", "success": False}

    def get_dataframe(self, object_name: str, workspace_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve a dataframe from R workspace

        Args:
            object_name: Name of the R object (e.g., "my_data", "df")
            workspace_path: Path to .RData file (optional)

        Returns:
            Dict with dataframe as pandas DataFrame
        """
        r_code = f"""
        # Load workspace if specified
        workspace_file <- commandArgs(trailingOnly = TRUE)[1]
        obj_name <- commandArgs(trailingOnly = TRUE)[2]
        output_file <- commandArgs(trailingOnly = TRUE)[3]

        if (!is.na(workspace_file) && file.exists(workspace_file)) {{
            load(workspace_file)
        }}

        # Check if object exists
        if (!exists(obj_name)) {{
            stop(paste("Object", obj_name, "not found in workspace"))
        }}

        # Get object
        obj <- get(obj_name)

        # Convert to dataframe if needed
        if (!is.data.frame(obj)) {{
            if (is.matrix(obj)) {{
                obj <- as.data.frame(obj)
            }} else if (is.vector(obj)) {{
                obj <- data.frame(value = obj)
            }} else {{
                stop(paste("Object", obj_name, "cannot be converted to dataframe"))
            }}
        }}

        # Write to CSV
        write.csv(obj, output_file, row.names = FALSE)

        # Print success
        cat(jsonlite::toJSON(list(
            success = TRUE,
            rows = nrow(obj),
            columns = ncol(obj),
            column_names = colnames(obj)
        ), auto_unbox = TRUE))
        """

        try:
            # Create temp files
            r_script = self.temp_dir / "get_dataframe.R"
            csv_output = self.temp_dir / f"{object_name}.csv"

            r_script.write_text(r_code)

            # Run R script
            cmd = [self.r_executable, str(r_script)]
            if workspace_path:
                cmd.append(workspace_path)
            else:
                cmd.append("NA")
            cmd.extend([object_name, str(csv_output)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Parse R output
                r_info = json.loads(result.stdout)

                # Load CSV as pandas DataFrame
                df = pd.read_csv(csv_output)

                # Clean up temp file
                csv_output.unlink()

                return {
                    "success": True,
                    "object_name": object_name,
                    "dataframe": df,
                    "rows": r_info["rows"],
                    "columns": r_info["columns"],
                    "column_names": r_info["column_names"],
                    "preview": df.head(5).to_dict('records')
                }
            else:
                return {
                    "error": f"R execution failed: {result.stderr}",
                    "success": False
                }

        except subprocess.TimeoutExpired:
            return {"error": "R script timed out after 30 seconds", "success": False}
        except Exception as e:
            return {"error": f"Failed to retrieve R dataframe: {str(e)}", "success": False}

    def execute_and_capture(self, r_code: str, capture_objects: List[str]) -> Dict[str, Any]:
        """
        Execute R code and capture specified objects

        Args:
            r_code: R code to execute
            capture_objects: List of object names to capture after execution

        Returns:
            Dict with captured objects as pandas DataFrames
        """
        full_r_code = f"""
        # Execute user code
        {r_code}

        # Capture specified objects
        output_dir <- commandArgs(trailingOnly = TRUE)[1]
        capture_names <- c({', '.join([f'"{name}"' for name in capture_objects])})

        captured <- list()

        for (obj_name in capture_names) {{
            if (exists(obj_name)) {{
                obj <- get(obj_name)

                # Save as CSV if dataframe-like
                if (is.data.frame(obj) || is.matrix(obj)) {{
                    filepath <- file.path(output_dir, paste0(obj_name, ".csv"))
                    write.csv(as.data.frame(obj), filepath, row.names = FALSE)
                    captured[[obj_name]] <- list(
                        type = "dataframe",
                        filepath = filepath,
                        rows = nrow(obj),
                        columns = ncol(obj)
                    )
                }} else if (is.vector(obj)) {{
                    captured[[obj_name]] <- list(
                        type = "vector",
                        value = obj,
                        length = length(obj)
                    )
                }} else {{
                    captured[[obj_name]] <- list(
                        type = class(obj)[1],
                        value = as.character(obj)
                    )
                }}
            }}
        }}

        # Output results as JSON
        cat(jsonlite::toJSON(captured, auto_unbox = TRUE))
        """

        try:
            # Create temp directory for outputs
            output_dir = self.temp_dir / "captures"
            output_dir.mkdir(exist_ok=True)

            # Write and execute R script
            r_script = self.temp_dir / "execute_and_capture.R"
            r_script.write_text(full_r_code)

            result = subprocess.run(
                [self.r_executable, str(r_script), str(output_dir)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                captured_info = json.loads(result.stdout)

                # Load dataframes
                captured_objects = {}
                for obj_name, info in captured_info.items():
                    if info["type"] == "dataframe":
                        df = pd.read_csv(info["filepath"])
                        captured_objects[obj_name] = {
                            "type": "dataframe",
                            "data": df,
                            "rows": info["rows"],
                            "columns": info["columns"]
                        }
                        # Clean up temp file
                        Path(info["filepath"]).unlink()
                    else:
                        captured_objects[obj_name] = info

                return {
                    "success": True,
                    "captured": captured_objects,
                    "stdout": result.stdout,
                    "stderr": result.stderr if result.stderr else None
                }
            else:
                return {
                    "error": f"R execution failed: {result.stderr}",
                    "success": False
                }

        except subprocess.TimeoutExpired:
            return {"error": "R script timed out after 60 seconds", "success": False}
        except Exception as e:
            return {"error": f"Failed to execute R code: {str(e)}", "success": False}

    def save_workspace(self, output_path: str, objects: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Save current R workspace (or specific objects) to .RData file

        Args:
            output_path: Where to save .RData file
            objects: List of object names to save (None = save all)

        Returns:
            Success status and file info
        """
        if objects:
            obj_list = ', '.join([f'"{obj}"' for obj in objects])
            r_code = f"""
            save(list = c({obj_list}), file = "{output_path}")
            cat("Saved", length(c({obj_list})), "objects to {output_path}")
            """
        else:
            r_code = f"""
            save.image("{output_path}")
            cat("Saved all workspace objects to {output_path}")
            """

        try:
            r_script = self.temp_dir / "save_workspace.R"
            r_script.write_text(r_code)

            result = subprocess.run(
                [self.r_executable, str(r_script)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": result.stdout,
                    "filepath": output_path
                }
            else:
                return {
                    "error": f"Failed to save workspace: {result.stderr}",
                    "success": False
                }

        except Exception as e:
            return {"error": f"Failed to save workspace: {str(e)}", "success": False}
