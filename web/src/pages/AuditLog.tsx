import { useState, useEffect } from "react";
import axios from "axios";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import ActivityIndicator from "@/components/indicators/activity-indicator";

type AuditLogEntry = {
  id: string;
  user_id: string;
  type: string;
  action: string;
  resource_id: string;
  start_time: number;
  end_time?: number;
  metadata: any;
};

export default function AuditLog() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const limit = 50;

  const fetchLogs = async (offset: number) => {
    setLoading(true);
    try {
      const response = await axios.get("audit/logs", {
        params: { limit, offset },
      });
      if (response.status === 200) {
        if (offset === 0) {
          setLogs(response.data);
        } else {
          setLogs((prev) => [...prev, ...response.data]);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs(0);
  }, []);

  const loadMore = () => {
    const newPage = page + 1;
    setPage(newPage);
    fetchLogs(newPage * limit);
  };

  return (
    <div className="flex h-full w-full flex-col p-4">
      <h1 className="mb-4 text-2xl font-bold">Audit Logs</h1>
      <div className="flex-1 overflow-auto border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Time</TableHead>
              <TableHead>User</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Resource</TableHead>
              <TableHead>Metadata</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {logs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>
                  {new Date(log.start_time * 1000).toLocaleString()}
                </TableCell>
                <TableCell>{log.user_id}</TableCell>
                <TableCell>{log.type}</TableCell>
                <TableCell>{log.action}</TableCell>
                <TableCell>{log.resource_id}</TableCell>
                <TableCell>
                  {log.metadata ? (
                    <pre className="text-xs">
                      {JSON.stringify(log.metadata, null, 2)}
                    </pre>
                  ) : null}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="mt-4 flex justify-center">
        <Button onClick={loadMore} disabled={loading}>
          {loading ? <ActivityIndicator className="size-4 mr-2" /> : null}
          Load More
        </Button>
      </div>
    </div>
  );
}
