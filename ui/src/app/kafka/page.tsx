"use client";

import { Database, Plus } from "lucide-react";

interface KafkaTopic {
  name: string;
  partitions: number;
  replicationFactor: number;
  retentionMs: number;
  messagesPerSec: number;
  consumerGroups: number;
}

const mockTopics: KafkaTopic[] = [
  { name: "orders.events", partitions: 6, replicationFactor: 3, retentionMs: 604800000, messagesPerSec: 1250, consumerGroups: 3 },
  { name: "payments.processed", partitions: 3, replicationFactor: 3, retentionMs: 259200000, messagesPerSec: 450, consumerGroups: 2 },
  { name: "user.notifications", partitions: 3, replicationFactor: 3, retentionMs: 86400000, messagesPerSec: 890, consumerGroups: 1 },
  { name: "audit.logs", partitions: 12, replicationFactor: 3, retentionMs: 2592000000, messagesPerSec: 3200, consumerGroups: 2 },
  { name: "inventory.updates", partitions: 6, replicationFactor: 3, retentionMs: 604800000, messagesPerSec: 200, consumerGroups: 4 },
];

function formatRetention(ms: number): string {
  const days = ms / (1000 * 60 * 60 * 24);
  return `${days}d`;
}

export default function KafkaPage() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Manage Kafka topics via Strimzi KafkaTopic CRDs
        </p>
        <button className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Plus className="h-4 w-4" />
          Create Topic
        </button>
      </div>

      <div className="rounded-lg border border-border bg-card">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left text-xs font-medium text-muted-foreground">
              <th className="px-4 py-3">Topic</th>
              <th className="px-4 py-3">Partitions</th>
              <th className="px-4 py-3">Replication</th>
              <th className="px-4 py-3">Retention</th>
              <th className="px-4 py-3">Throughput</th>
              <th className="px-4 py-3">Consumers</th>
            </tr>
          </thead>
          <tbody>
            {mockTopics.map((topic) => (
              <tr key={topic.name} className="border-b border-border last:border-0 hover:bg-muted/50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">{topic.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">{topic.partitions}</td>
                <td className="px-4 py-3 text-sm">{topic.replicationFactor}</td>
                <td className="px-4 py-3 text-sm">{formatRetention(topic.retentionMs)}</td>
                <td className="px-4 py-3 text-sm">{topic.messagesPerSec.toLocaleString()} msg/s</td>
                <td className="px-4 py-3 text-sm">{topic.consumerGroups}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
